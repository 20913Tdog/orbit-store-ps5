#include "orbit.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* Exercise the real browser worker and the production provider URL policy.
 * Only storage, network I/O and the final queue write are fixtures. */
Orbit orbit = {.mutex = PTHREAD_MUTEX_INITIALIZER};
static Release selected, queued;
static Storage destination = {.id = "internal", .root = "/fixture", .device = 1, .inode = 2};
static Job job;
static bool enabled = true;
static unsigned created, refreshed;
static atomic_bool hold_validation, validation_entered;
static bool fail_validation;
static const char *direct = "https://vikingfile.com/d/Abcd123456/PPSA00001-fixture.ffpfsc";

void copy_text(char *to, size_t cap, const char *s) { snprintf(to, cap, "%s", s ? s : ""); }
const char *json_text(const cJSON *o, const char *key) {
    const cJSON *v = cJSON_GetObjectItemCaseSensitive(o, key);
    return cJSON_IsString(v) ? v->valuestring : "";
}
void random_hex(char *out, size_t bytes) { memset(out, 'a', bytes * 2); out[bytes * 2] = 0; }
Release *release_find(const char *id) { return !strcmp(id, selected.id) ? &selected : NULL; }
Job *job_find(const char *id) { return job.id[0] && !strcmp(id, job.id) ? &job : NULL; }
bool source_enabled_locked(const Release *r) { (void)r; return enabled; }
size_t storage_list(Storage *out) { *out = destination; return 1; }
bool job_can_refresh_link(const Job *j) { return j && !strcmp(j->status, "paused"); }
int job_check_capture_locked(const Release *r, const Storage *s, char *error, size_t cap) {
    (void)r; (void)s;
    if (enabled) return 200;
    copy_text(error, cap, "Source disabled."); return 409;
}
int job_create_captured_locked(const Release *r, const Storage *s, const char *etag,
        const char *modified, char *error, size_t cap, Job **result) {
    (void)s; (void)modified; (void)error; (void)cap;
    assert(!strcmp(etag, "\"fixture\""));
    queued = *r; created++;
    copy_text(job.id, sizeof job.id, "fixture-job"); *result = &job;
    return 201;
}
int job_refresh_link_locked(Job *j, const Release *r, const Storage *s, const char *etag,
        const char *modified, char *error, size_t cap) {
    (void)s; (void)modified; (void)error; (void)cap;
    assert(j == &job && j->received == 1024 && !strcmp(etag, "\"fixture\""));
    queued = *r; refreshed++; return 200;
}
static void tick(void) { struct timespec t = {.tv_nsec = 1000000}; nanosleep(&t, NULL); }
int transfer_validate_capture(Release *r, atomic_bool *cancel, char *etag,
        char *modified, char *error, size_t cap) {
    (void)modified;
    assert(!strcmp(r->url, direct));
    atomic_store(&validation_entered, true);
    for (unsigned i = 0; atomic_load(&hold_validation) && i < 5000; i++) tick();
    assert(!atomic_load(&hold_validation));
    if (atomic_load(cancel)) return 1;
    if (fail_validation) { copy_text(error, cap, "File identity mismatch."); return 1; }
    copy_text(etag, 256, "\"fixture\""); return 0;
}
static cJSON *request(const char *action, bool with_link) {
    cJSON *o = cJSON_CreateObject();
    cJSON_AddStringToObject(o, "action", action);
    cJSON_AddStringToObject(o, "releaseId", selected.id);
    cJSON_AddStringToObject(o, "storageId", destination.id);
    cJSON_AddStringToObject(o, "jobId", job.id);
    if (with_link) cJSON_AddStringToObject(o, "directUrl", direct);
    return o;
}
static int submit(cJSON *o) {
    char error[256] = {0}; int code = browser_action(o, error, sizeof error);
    cJSON_Delete(o); return code;
}
static void wait_validation(void) {
    for (unsigned i = 0; i < 5000 && !atomic_load(&validation_entered); i++) tick();
    assert(atomic_load(&validation_entered));
}
static void expect_state(const char *state) {
    for (unsigned i = 0; i < 5000; i++) {
        cJSON *s = browser_status();
        bool active = cJSON_IsTrue(cJSON_GetObjectItemCaseSensitive(s, "active"));
        if (!active) {
            if (strcmp(json_text(s, "state"), state)) {
                char *text = cJSON_PrintUnformatted(s); fprintf(stderr, "%s\n", text); free(text);
            }
            assert(!strcmp(json_text(s, "state"), state));
            char *text = cJSON_PrintUnformatted(s); assert(!strstr(text, "https://")); free(text);
            cJSON_Delete(s); return;
        }
        cJSON_Delete(s); tick();
    }
    assert(!"worker timeout");
}
static void rejects(void) {
    const char *bad[] = {"", "https://vikingfile.com/f/Abcd123456",
        "https://vikingfile.com/d/Abcd123456/other.ffpfsc",
        "http://vikingfile.com/d/Abcd123456/PPSA00001-fixture.ffpfsc",
        "https://127.0.0.1/d/Abcd123456/PPSA00001-fixture.ffpfsc",
        "https://vikingfile.com.evil.test/d/Abcd123456/PPSA00001-fixture.ffpfsc",
        "https://user@vikingfile.com/d/Abcd123456/PPSA00001-fixture.ffpfsc",
        "https://vikingfile.com/d/Abcd123456/PPSA00001-fixture.ffpfsc?extra=1",
        "https://vikingfile.com/d/Abcd123456/PPSA00001-fixture.ffpfsc#fragment",
        "https://vikingfile.com/d/Abcd123456/%2e%2e%2fPPSA00001-fixture.ffpfsc"};
    for (size_t i = 0; i < sizeof bad / sizeof bad[0]; i++) {
        cJSON *o = request("start", false); cJSON_AddStringToObject(o, "directUrl", bad[i]);
        assert(submit(o) == 400);
    }
    const char *types[] = {"null", "true", "123", "[]", "{}"};
    for (size_t i = 0; i < sizeof types / sizeof types[0]; i++) {
        cJSON *o = request("start", false);
        cJSON_AddItemToObject(o, "directUrl", cJSON_Parse(types[i])); assert(submit(o) == 400);
    }
    char huge[3000]; memset(huge, 'a', sizeof huge - 1); huge[sizeof huge - 1] = 0;
    cJSON *o = request("start", false); cJSON_AddStringToObject(o, "directUrl", huge);
    assert(submit(o) == 400);
    o = request("start", true); cJSON_ReplaceItemInObject(o, "storageId", cJSON_CreateString("missing"));
    assert(submit(o) == 409);
    enabled = false; assert(submit(request("start", true)) == 409);
    assert(!created && !refreshed && !atomic_load(&validation_entered));
}
int main(int argc, char **argv) {
    assert(argc == 2);
    copy_text(selected.id, sizeof selected.id, "pc-fixture");
    copy_text(selected.title_id, sizeof selected.title_id, "PPSA00001");
    copy_text(selected.filename, sizeof selected.filename, "PPSA00001-fixture.ffpfsc");
    copy_text(selected.format, sizeof selected.format, "FFPFSC");
    copy_text(selected.source, sizeof selected.source, "vikingfile");
    copy_text(selected.browser_url, sizeof selected.browser_url, "https://vikingfile.com/f/Abcd123456");
    copy_text(selected.url, sizeof selected.url, selected.browser_url);
    selected.size = 4096;
    assert(browser_start() == 0);
    const char *scenario = argv[1];
    if (!strcmp(scenario, "rejects")) { rejects(); browser_stop(); return 0; }
    bool refresh = !strncmp(scenario, "refresh", 7);
    if (refresh) {
        job.release = selected; job.received = 1024; job.device = 1; job.inode = 2;
        copy_text(job.id, sizeof job.id, "paused-job");
        copy_text(job.status, sizeof job.status, "paused");
        copy_text(job.storage_id, sizeof job.storage_id, destination.id);
        copy_text(job.root, sizeof job.root, destination.root);
    }
    bool legacy = !strcmp(scenario, "legacy");
    if (legacy) assert(setenv("ORBIT_TEST_CAPTURE_URL", direct, 1) == 0);
    else unsetenv("ORBIT_TEST_CAPTURE_URL");
    bool held = !strcmp(scenario, "cancel") || !strcmp(scenario, "source-change") ||
        !strcmp(scenario, "catalog-change") || !strcmp(scenario, "refresh-change") || !strcmp(scenario, "busy");
    atomic_store(&hold_validation, held);
    fail_validation = !strcmp(scenario, "identity-mismatch");
    assert(submit(request(refresh ? "refresh" : "start", !legacy)) == 202);
    if (held) {
        wait_validation();
        if (!strcmp(scenario, "cancel")) {
            cJSON *s = browser_status(), *o = request("cancel", false);
            cJSON_AddStringToObject(o, "id", json_text(s, "id"));
            cJSON_Delete(s); assert(submit(o) == 202);
        } else if (!strcmp(scenario, "busy")) assert(submit(request("start", true)) == 409);
        else {
            pthread_mutex_lock(&orbit.mutex);
            if (!strcmp(scenario, "source-change")) { enabled = false; browser_source_changed_locked(); }
            if (!strcmp(scenario, "catalog-change")) selected.size++;
            if (!strcmp(scenario, "refresh-change")) job.received++;
            pthread_mutex_unlock(&orbit.mutex);
        }
        atomic_store(&hold_validation, false);
    }
    bool cancelled = !strcmp(scenario, "cancel") || !strcmp(scenario, "source-change");
    bool failed = fail_validation || !strcmp(scenario, "catalog-change") || !strcmp(scenario, "refresh-change");
    expect_state(cancelled ? "cancelled" : failed ? "failed" : "queued");
    browser_stop();
    assert(created + refreshed == (unsigned)(!cancelled && !failed));
    if (!cancelled && !failed) {
        assert(!strcmp(queued.url, direct)); assert(queued.size == 4096);
        assert(refreshed == (unsigned)refresh);
        assert(!strcmp(selected.url, selected.browser_url));
    }
    return 0;
}
