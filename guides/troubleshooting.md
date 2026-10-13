# When something needs attention

## I see two Orbit icons

That's normal if you use both PS5 versions. The icon in **Games** is the TV app from `PPSA99177.ffpkg`. The icon in **Media** is the browser version, added when `orbit_store.elf` runs. Both use the same downloads, favourites and settings.

If the Media icon won't open, see the next section. If the Games icon won't open, see [The native TV app will not open or start Orbit](#the-native-tv-app-will-not-open-or-start-orbit).

## Orbit or its icon does not open

Start the Orbit payload through your manager, then reopen the Media-tab icon. The icon opens a running Orbit server and cannot start a stopped payload. If the icon was deleted, starting Orbit recreates it. Keep Orbit’s saved data when updating.

From another device, use `http://<ps5-ip>:34177/` on the same local network. Keep that port private to your LAN.

## The native TV app will not open or start Orbit

The Games-row app needs **kstuff and ShadowMountPlus**. Check that `PPSA99177.ffpkg` is in `/data/homebrew/` and let ShadowMountPlus register it. Keep only one FFPKG or folder installation.

If the app says Orbit is not running, start your ELF loader on **port 9021** and choose **Try again**, or launch `orbit_store.elf` through your payload manager. The app never stops another running payload to make room.

For missing artwork in the TV app, check the running service version in the browser's **App settings → Update / reinstall**. Use **0.6.0 or later**; older services cannot load artwork for the TV app. Stop Orbit and start the updated service. Installing the new FFPKG alone does not replace a service already running.

If ShadowMount reports **TitleDir bridge unavailable**, its app-registration bridge is not ready. Close active games, restart the console when convenient, run your usual jailbreak and ShadowMount setup, then retry registration of the existing FFPKG. If it persists, include ShadowMount's version and the relevant registration errors from its debug log in your report.

If a TV app update still opens the previous version, close the app first. Restart the console and jailbreak when convenient so ShadowMountPlus can remount the replacement. The TV app and service have separate versions.

## Orbit shows BlackBox's icon, can't connect or is missing after BlackBox

BlackBox's builds up to v1.0.6 use Orbit's title ID, `ORBT00001`. If you installed one of them, Orbit's Media-tab icon may show BlackBox's logo, fail with "127.0.0.1 could not reach", or not appear at all. Removing BlackBox's payload alone doesn't fix this, because its app files stay on the console. These steps come from users who fixed it ([#42](https://github.com/saawant12/orbit-store-ps5/issues/42), [#39](https://github.com/saawant12/orbit-store-ps5/issues/39)).

You need FTP access to the PS5, for example `ftpsrv` from your payload manager and FileZilla on a computer (port 2121). Delete only the items listed here.

1. **Stop BlackBox from starting.** Remove `blackbox.elf` from your payload manager and turn off its auto-start.
2. **Delete the home-screen icons.** On the PS5, delete BlackBox's icon from the Games row and Orbit's icon from the Media tab. Orbit's icon comes back in step 5.
3. **Delete BlackBox's files over FTP:**
   - `/user/app/BLKB00001`
   - `PPSA01453` in `/data/homebrew/` (its TV app, a `.ffpkg` file or a folder)
   - `/user/download/PPSA01453`
   - `/data/shadowmount/icon-cache/PPSA01453*.png`
   - its payload-manager folder, such as `/data/pldmgr/payloads/BlackBox`
4. **Delete Orbit's icon folder, `/user/app/ORBT00001`.** Orbit rebuilds it the next time it starts. Keep `/data/orbit-store`: it holds your download queue and settings.
5. **Restart and start Orbit.** Restart the console, run your jailbreak, then start `orbit_store.elf`. Open Orbit from the Media tab, or open the TV app from the Games row, which needs kstuff and ShadowMountPlus.

If Orbit still shows BlackBox's icon, open a bug report with your firmware, your Orbit version and what you deleted.

## An update says Orbit is already running

The replacement was saved for the next start. Open **App settings → Update / reinstall**, compare **Running** and **Saved for next start**, choose **Stop Orbit to restart**, then launch the saved `/data/orbit-store/orbit_store.elf` or a synced manager copy. Pairing and the queue stay saved. A manually imported old ELF starts that older copy unless you replace it.

## AkiraBox does not enter Downloads

Use matching Orbit Store or Orbit Zero **1.2.0** apps. Open the file page from Orbit, complete verification and wait a few seconds without pressing Download. Orbit captures the ready link; avoid advertisements and popup buttons. If the session expires, return to Orbit and open the provider step again. For a paused or failed job, use **Refresh download link**.

## Archive needs a password

Orbit automatically tries the [known source passwords](../README.md#automatic-archive-extraction-120). If the archive needs a different one, choose **Enter archive password**, enter the source’s password exactly, then **Retry extraction**. Keep the downloaded archive and enough free space for its extracted files. A corrupt or unsupported archive can still fail with the correct password.

## Vikingfile does not enter Downloads

Use Orbit 0.5.0 or later and enable Vikingfile in Sources. Select the desired option and drive, press **Open download page on PS5**, complete any provider verification and press Download on the provider page, then return to Orbit. Verification happens on the PS5 even if you initiated it on your phone.

If the session times out, the provider page changes or the browser restarts, return to Orbit and try that option again. Cancel an existing session before starting another. A file that does not match the selected option is not queued. Provider links may become unavailable.

## Internal storage or an M.2 SSD is missing

If the drive disappeared after updating to 0.9.0, install **Orbit 1.0.0 or later**, restart the download service and refresh storage. Native app users should also update the TV app to **1.3.0 or later**, which includes the fixed service. Replacing the FFPKG alone does not replace a service that is already running.

An available drive appears even if its `homebrew` folder has not been created yet. Orbit creates the folder when needed and checks actual write access when a download starts or resumes. If the destination cannot be written, the download stops and existing partial data is kept.

If the drive still does not appear, include your firmware, Orbit and ShadowMount versions and a fresh diagnostic report in your bug report.

## A download fails or is slow

- **Provider returned a page:** update Orbit, restart it and retry from Downloads. For browser-only Vikingfile options, repeat the provider step. Orbit still rejects an actual error or verification page returned instead of file data.
- **Provider throttling:** let the retry delay finish. Orbit honours the provider’s Retry-After response.
- **Drive disconnected:** reconnect the original destination. Orbit does not silently switch to a different drive.
- **Not enough space:** free space on the chosen destination, considering unfinished downloads, then retry.
- **Source changed:** keep the partial until you decide whether to remove it and restart. Orbit will not append a different file to it.

Parallel connections can help only when supported by the host and file identity. Provider speed limits, network conditions and drive performance still apply.

## An Orbit Zero transfer is stuck after sleep or disconnection

Wake the computer and PS5, keep the original destination connected, and reconnect in **Console**. Start Orbit on the PS5 if its service stopped. Keep the original pairing and computer partial file, then select **Resume** on the interrupted transfer. Orbit checks the saved files before continuing; it does not start every paused transfer automatically.

If other games show **Waiting to transfer**, an earlier PS5 transfer may still hold their turn. In Downloads, choose the recovery action that matches what you want:

- **Resume** to continue that transfer.
- **Cancel and remove partials** to delete its unfinished files after confirmation and start fresh.
- **Stop transfer** to keep remaining files and free the queue. **A stopped transfer cannot resume afterward.**

For a transfer already created on the PS5, cancellation and stopping need a response from the original console. If it cannot confirm the operation, reconnect and retry. If Zero asks for a newer receiver, update both the desktop app and the PS5 service using [these steps](orbit-zero-installation.md#update-orbit-zero). The receiver is `orbit_store.elf`; installing only the desktop update does not replace a running PS5 service.

Keep both devices awake while transferring. See [transfer recovery and cleanup](orbit-zero.md#pause-reconnect-and-clean-up) for the differences between stopping, deleting partials and clearing completed computer copies.

## A game or image is missing

Check the enabled Sources and clear Browse’s filters. Then try **App settings → Game catalogue → Refresh catalogue**. Use the latest matching apps; PS4 support starts with service 1.1.0, native app 1.4.0 and Orbit Zero 1.1.0. Builds without PS4 support use a PS5-compatible catalogue. Select **Platform → All platforms** or **PS4**, and check the running service version as well as the installed app version.

Artwork comes from external URLs. Orbit tries an available fallback when the primary fails. Network/DNS restrictions or unavailable host images can still prevent artwork from loading. Some dates and other metadata remain missing; corrections arrive through catalogue updates. Undated games appear after dated games in release-date sorting.

## A completed download is missing from Library

For downloads handled by Orbit Store, check **Downloads → Finished → Location** in the browser or native app. Use a file manager to check that exact saved path on the selected drive. Extracted downloads may be a folder containing several files. The recorded path remains in history even if a file is later moved or deleted.

Orbit Zero download details also show the full PS5 destination path and the computer path while a cached copy remains. Check the selected PS5 drive's [homebrew folder](downloads.md#where-downloads-are-saved). The computer download finishing is not enough; wait for **Transfer to PS5** to complete too.

If the file exists but does not appear in Library or on the home screen, check its format and the installation or mounting method supported by your console setup. A finished download is not automatically installed, and ShadowMount may not list every format. PKG and FPKG packages need installing first; see [below](#a-downloaded-pkg-or-fpkg-game-doesnt-appear). If the file is absent, include the app, game, source, format, destination and completion screen in your report; do not delete the queue or remaining files while investigating.

## A downloaded PKG or FPKG game doesn't appear

PKG and FPKG options are `.pkg` packages, for PS4 or PS5 games. Orbit saves them to the chosen drive's `homebrew` folder; it doesn't install them. ShadowMountPlus doesn't mount packages, so a package won't appear in Library or on the home screen, and **Scan for games** won't find it. Install it with the package installer supported by your PS5 setup, and check that installer's firmware support. PS5 FPKG games currently run only on firmware 11.60 or lower (October 2026); on 12.xx and 13.xx they may install but won't start. Copying a game package to the same folder as Orbit's native app does not register it the way the TV app is registered.

If the game also offers exFAT or FFPFSC, those are mounted by ShadowMountPlus without installing. See [which format to pick](downloads.md#which-format-to-pick).

If you report a problem, include the title ID (`CUSA` for PS4, `PPSA` for PS5), source, format, destination, app versions, any error code from the installer, and whether it fails during the computer download, PS5 transfer or package installation. Do not share temporary signed links. See [PS4 games on PS5](downloads.md#ps4-games-on-ps5).

## Share a diagnostic report

Open **App settings → Diagnostics → View diagnostics**, then **Copy diagnostic report**. If automatic copying is unavailable, Orbit shows selectable report text. Reports omit pairing codes, access tokens, download links, game names and paths. Nothing is sent automatically.

![App settings with local diagnostics](../assets/0.9.0/desktop-diagnostics.jpg)

*You choose whether to copy and share a report. This interface preview uses example diagnostic data.*

When reporting a problem in [Issues](https://github.com/saawant12/orbit-store-ps5/issues), include the Orbit version, PS5 firmware, loader, the steps taken and the displayed error. Remove any private details before posting. The reported etaHEN payload-toggle interaction remains under investigation.

[Getting started](getting-started.md) · [Download guide](downloads.md) · [Library guide](library.md) · [Project home](../README.md)
