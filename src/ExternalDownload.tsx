import { useId, useState } from "react";
import { api } from "./api";
import { t } from "./i18n";
import type { Release } from "./types";

export function OpenSourceButton({ release, disabled, onBusyChange }: {
  release: Release;
  disabled: boolean;
  onBusyChange: (busy: boolean) => void;
}) {
  const [opening, setOpening] = useState(false);
  const [error, setError] = useState("");

  async function openPage() {
    // Open synchronously from the click so the browser's popup blocker can
    // distinguish this requested tab from advertisements on the provider page.
    const tab = window.open("about:blank", "_blank");
    if (tab) tab.opener = null;
    setOpening(true);
    onBusyChange(true);
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
      onBusyChange(false);
    }
  }

  return (
    <div className="source-file-actions">
      <button type="button" className="source-file-button" disabled={disabled || opening} onClick={() => void openPage()}>
        {opening ? t("Please wait…") : t("Open source file")}
      </button>
      {error && <p className="form-error" role="alert">{error}</p>}
    </div>
  );
}

export function ExternalDownload({ release, value, onChange, disabled }: {
  release: Release;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
}) {
  const inputId = useId();
  return (
    <section className="external-download" id="provider-browser-steps" aria-labelledby={`${inputId}-title`}>
      <h3 id={`${inputId}-title`}>{t("Use a download link from your computer")}</h3>
      <p>{t("Complete verification in your computer’s browser, then paste the final file URL below. Your PS5 downloads the file directly.")}</p>
      <div className="external-download-field">
        <label htmlFor={inputId}>{t("Direct download link")}</label>
        <input id={inputId} type="url" maxLength={2047}
          value={value} onChange={event => onChange(event.target.value)}
          disabled={disabled} autoComplete="off" spellCheck={false}
          placeholder="https://…" />
        <p className="external-download-hint">{t("Leave the link empty to open the download page on your PS5.")}</p>
        <small>{t("The link must point to this file:")} <span>{release.filename}</span></small>
      </div>
    </section>
  );
}
