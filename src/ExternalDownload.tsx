import { useId, useState, type FormEvent } from "react";
import { api } from "./api";
import { t } from "./i18n";
import type { Release } from "./types";

export function ExternalDownload({ release, disabled, submit }: {
  release: Release;
  disabled: boolean;
  submit: (url: string) => Promise<void>;
}) {
  const inputId = useId();
  const [url, setUrl] = useState("");
  const [opening, setOpening] = useState(false);
  const [error, setError] = useState("");

  async function openPage() {
    // Open synchronously from the click so the browser's popup blocker can
    // distinguish this requested tab from advertisements on the provider page.
    const tab = window.open("about:blank", "_blank");
    if (tab) tab.opener = null;
    setOpening(true);
    setError("");
    try {
      const page = await api<{ url: string }>(`/browser/page?releaseId=${encodeURIComponent(release.id)}`);
      const target = new URL(page.url);
      if (target.protocol !== "https:" || target.username || target.password)
        throw new Error(t("This option has no supported provider browser page."));
      if (!tab) {
        throw new Error(t("Allow the download page to open in a new tab, then try again."));
      }
      tab.location.replace(target.href);
    } catch (e) {
      tab?.close();
      setError((e as Error).message);
    } finally {
      setOpening(false);
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (disabled || opening || !url.trim()) return;
    await submit(url.trim());
  }

  return (
    <details className="external-download">
      <summary>{t("Use a download link from your computer")}</summary>
      <p>{t("Complete verification in your computer’s browser, then paste the final file URL below. Your PS5 downloads the file directly.")}</p>
      <button type="button" disabled={disabled || opening} onClick={() => void openPage()}>
        {opening ? t("Please wait…") : t("Open download page on this computer")}
      </button>
      <form onSubmit={event => void onSubmit(event)}>
        <label htmlFor={inputId}>{t("Direct download link")}</label>
        <input id={inputId} type="url" required maxLength={2047}
          value={url} onChange={event => setUrl(event.target.value)}
          disabled={disabled || opening} autoComplete="off" spellCheck={false}
          placeholder="https://…" />
        <small>{t("The link must point to this file:")} <span>{release.filename}</span></small>
        <button type="submit" disabled={disabled || opening || !url.trim()}>{t("Download to PS5")}</button>
      </form>
      {error && <p role="alert">{error}</p>}
    </details>
  );
}
