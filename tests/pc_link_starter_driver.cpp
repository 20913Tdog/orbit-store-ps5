#include "orbit/starter.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <string>
#include <unistd.h>

int main() {
    char directory[] = "/tmp/orbit-pc-starter-XXXXXX";
    assert(mkdtemp(directory));
    const std::filesystem::path root(directory);
    orbit::starter::Locations locations;
    locations.saved_elf = (root / "saved.elf").string();
    locations.saved_version = (root / "saved-version.txt").string();
    locations.bundled_elf = (root / "bundled.elf").string();
    locations.bundled_version = (root / "bundled-version.txt").string();
    char elf[64] = {0x7f, 'E', 'L', 'F', 2, 1};
    elf[18] = 62;
    for (const auto &path : {locations.saved_elf, locations.bundled_elf})
        std::ofstream(path, std::ios::binary).write(elf, sizeof elf);
    std::ofstream(locations.saved_version) << "1.3.6-beta.1\n";
    std::ofstream(locations.bundled_version) << "1.3.5\n";
    assert(orbit::starter::compare_versions("1.3.6-beta.1", "1.3.5") > 0);
    assert(orbit::starter::choose(locations).path == locations.saved_elf);
    std::ofstream(locations.bundled_version) << "1.3.6\n";
    assert(orbit::starter::choose(locations).path == locations.bundled_elf);
    std::filesystem::remove_all(root);
}
