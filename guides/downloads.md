# Find and download a game

Orbit 1.2.0 includes **1,201 games: 801 PS5 games and 400 PS4 games**, with single-file options from Archive.org, Vikingfile and AkiraBox. Each platform edition has its own game page; open it to choose from its available sources and formats. The selection depends on which sources you enable.

## Browse and choose

**Discover opens first.** Explore the featured game and **New on Orbit** first, followed by **Latest releases**. New on Orbit starts with selected highlights, then shows recent additions ordered by game release date. Move down to All games for the full collection. Its grid shows 96 games per page, largest downloads first. Each game's size is its smallest available option from your enabled sources. Use Previous and Next to move between pages.

![Native Discover with the 1.2.0 catalogue](../assets/1.2.0/native-discover.png)

*Native Discover with the 1.2.0 catalogue, rendered locally from the app. Browser and desktop Discover use the same featured order.*

Switch to **Browse** when you want search and filters. It defaults to **Release date (newest first)**. Games without a recorded date follow alphabetically. Search by game name or title ID, filter by platform, source, format, region or download size, and change the sort order. **Reset filters** restores the default. Missing dates and other metadata can be added later through catalogue updates.

![Native Browse with platform, source, format and region filters](../assets/1.1.0/native-browse.png)

*Use filters to find options that fit your drive and preferred format. Sizes reflect the download option you choose.*

Save a game from its details page to find it under **Favourites** later; favourites are shared with your paired devices.

In the native TV app, use D-pad/left stick to move, Cross to select, Circle to go back and L1/R1 to switch tabs. Press **Square** on a game selected in Browse or Discover to add or remove it from Favourites. Select filters with Cross; choose an option with the D-pad and Cross. The controls below apply to the browser version.

| Input | Action |
|---|---|
| D-pad or arrow keys | Move focus |
| Cross or Enter | Select the focused control |
| Circle or Escape | Go back or close a panel |
| Search: Down or Enter | Move into results |
| Search: Up | Return to the Browse tab |
| Search: Left or Right | Edit the text normally |
| Touch or mouse | Select a control |

## PS4 games on PS5

PS4 support starts with **Orbit Store 1.1.0**, **native app 1.4.0** and **Orbit Zero 1.1.0**. Use the latest matching apps for the current catalogue and features. Update the apps before refreshing the catalogue; builds without PS4 support keep their PS5-compatible catalogue.

1. Open **Browse → Platform → PS4**. Choose **All platforms** to see PS4 and PS5 together.
2. Open a game and check its **PS4** label, title ID, region and source notes. PS4 title IDs begin with `CUSA`; PS5 IDs begin with `PPSA`. Editions for different platforms stay separate, even when their names match.
3. Choose a **PKG** or **FPKG** option, its source and the destination drive. Both use a `.pkg` file; the format label describes the available package. A PS4 label does not imply a frame-rate patch, DLC, or compatibility with every PS5 setup. Check the specific option’s notes.
4. Follow the provider steps below. Orbit Zero can download and transfer these files while the PS5 has no internet access.

Files go to the selected drive’s `homebrew` folder, including `/data/homebrew/` for internal storage. A completed transfer saves the package; it does not install the game. Use the PS4 package installation method supported by your PS5 setup and check its game and firmware requirements. The instructions for installing Orbit’s own `PPSA99177.ffpkg` TV app do not install a downloaded game package.

**Orbit still runs on PS5.** PS4 game support does not make the ELF or TV app compatible with PS4 consoles. See [Library](library.md) for the distinction between downloaded files and installed games.

## Pick a source, format and drive

On the game page, select the main download button to open **Download options**. This reviews your choices without starting a transfer. Open **Source** to choose a format and provider, **Download using** for direct or TorBox delivery, and **Save to** for storage attached to the PS5. The storage panel shows **Free now**, **Unfinished downloads**, and **After queue + this download**. Back returns to your previous selection.

![Download options with source, delivery method and destination](../assets/0.9.0/desktop-details.jpg)

*Different sources can offer different formats or sizes for the same game. Select the exact option you intend to download.*

For a direct option, select **Download to PS5**. Orbit checks the file and destination, then adds it to Downloads.

## Where downloads are saved

Direct PS5 downloads and Orbit Zero transfers use the selected PS5 drive’s `homebrew` folder:

| Destination | Folder on the PS5 |
| --- | --- |
| Internal storage | `/data/homebrew/` |
| M.2 SSD | `/mnt/ext1/homebrew/` |
| USB drive | `/mnt/usb0/homebrew/`, `/mnt/usb1/homebrew/`, or the corresponding folder for the selected USB drive |

USB numbering depends on how the console mounts your drives. Choose by the storage label shown in Orbit and keep that drive connected. Orbit creates `homebrew` when needed and checks write access before downloading or resuming. A drive attached only to your computer is not a PS5 destination.

Orbit Zero also keeps a computer copy in your chosen [computer download folder](orbit-zero.md#choose-the-computer-download-folder), unless you enable cleanup after transfer. Saving a game package to the PS5 does not install it; use the tools supported by your console setup.

For downloads handled by Orbit Store, **Downloads → Finished → Location** shows the saved file or extracted folder path in both the browser and native app. This is the recorded save location; it does not check whether someone has since moved or deleted the file, and it does not mean the game is installed or listed by ShadowMount.

Orbit Zero currently shows the filename without the full PS5 path. Check the selected drive's `homebrew` folder. Extracted downloads may be a file or a folder containing several files. Zero's **Computer download folder** setting controls new computer downloads; existing partial files stay in their original folder.

## Optional: download through TorBox

**Available in 0.8.0 and later.** TorBox is an optional delivery choice for supported links. Update both Orbit’s service ELF and native FFPKG to use it in the TV app. You need your own TorBox account; its plan, host availability, quotas and file-size limits apply. You can keep using the original provider without connecting TorBox.

1. In Orbit’s browser version, open **App settings → Debrid**. You can do this on the PS5 or a paired phone or computer.
2. Get your API key from [TorBox settings](https://torbox.app/settings), enter it in Orbit and choose **Connect TorBox**. Keep the key private.
3. Open a game in either Orbit app and use its main button to open **Download options**. Select **Source**, then **Download using → TorBox**, and choose your destination drive.
4. Select **Download via TorBox**. Follow preparation and transfer progress in Downloads, where the job is labelled **via TorBox**.

![Browser Debrid settings with a sample connected TorBox account and an empty API-key field](../assets/0.9.0/desktop-torbox-setup.jpg)

*Connect the account in the browser once. The native TV app and paired devices share that connection. If you are not connected, choose **Set up TorBox** under a game’s **Download using** options. In the TV app this opens the browser with your game, source and destination selected; connect in App settings, then return to the game.*

![Game details with TorBox selected and a PS5 destination drive](../assets/0.9.0/desktop-torbox-details.jpg)

An account connection does not guarantee support for every file. If an option is unavailable through TorBox, select the original provider explicitly. Orbit does not silently switch a TorBox job to another delivery method.

Pause and resume from Downloads as usual. Disconnecting TorBox pauses its unfinished jobs and keeps their partial files. Reconnect the same account to resume them. Disconnecting does not remove files from your remote TorBox account.

## AkiraBox: verify, then wait

**Requires Orbit Store or Orbit Zero 1.2.0.** Choose the AkiraBox option and destination, then open its download page from Orbit. Complete any human verification yourself and wait a few seconds. **Do not press AkiraBox’s Download button or an advertisement.** Orbit captures the ready file link and checks it against your selected game.

In Orbit’s PS5 browser version, you return to Orbit automatically when the file is queued. If you started from the native TV app, return to the app to follow verification or view the download. In Orbit Zero, the provider window closes once the matching file is ready, and the download appears in your queue.

If the session expires, start the provider step again. For an existing paused or failed AkiraBox download, use **Refresh download link**. Orbit reuses the partial file only if the refreshed link identifies the same file.

## ZIP, RAR and 7z downloads

**Requires 1.2.0 and its matching apps.** Compressed options appear in the normal Format filter. Their displayed download size is the compressed archive size; keep space for both the archive and the extracted files. Multipart archives are not supported.

Orbit Store extracts on the selected PS5 drive after downloading. Orbit Zero extracts on the computer first, then transfers the extracted files to your selected PS5 drive. Follow the **Extracting** progress in Downloads. Orbit tries the known source passwords automatically; see the [password list](../README.md#automatic-archive-extraction-120). If another password is needed, choose **Enter archive password**, then **Retry extraction**. This reuses the downloaded archive.

**Delete archives after extracting** is on by default in both apps. Find it under **App settings → Storage** in Orbit Store, or **Downloads → Download settings** in Orbit Zero. It removes the downloaded archive after successful extraction and keeps archives that need a password or fail to extract.

In Zero, the extracted computer files follow the separate **Computer cache** setting. **Automatically remove after transfer** is off by default; enabling it removes those copies only after the PS5 confirms the transfer. Deleting an archive after extraction does not delete the extracted files. See [saved locations](#where-downloads-are-saved) to find the result.

## Simultaneous downloads

Orbit Store and Orbit Zero start one game at a time by default. Choose **1–8** in Orbit Store’s **App settings → Storage → Simultaneous downloads**, or **Downloads → Download settings → Simultaneous computer downloads** in Orbit Zero. Reducing the limit lets active downloads finish before another starts. Orbit Zero transfers one file to the PS5 at a time while computer downloads continue.

## Vikingfile: open the page on PS5 first

**Starting in the native TV app?** Open **Download options**, choose your source and drive, then select **Open Vikingfile on PS5**. Vikingfile opens directly in the PS5 browser. Complete any verification, select **Download** on the provider page, then return to the native Orbit Store app. Orbit checks the file and queues it on your selected drive. You do not need to open Orbit's browser interface first. If the source or drive is no longer available, choose an available one explicitly.

**Downloading through Orbit Zero?** Vikingfile opens on your computer instead. Complete any verification and select **Download** there. See the [Orbit Zero download steps](orbit-zero-installation.md#vikingfile-downloads).

**Requires Orbit 0.5.0 or later.** Older versions keep their Archive.org catalogue and do not receive unsupported Vikingfile options.

1. Select the Vikingfile option and destination drive in Orbit.
2. Select **Open download page on PS5** in Orbit's browser interface, or **Open Vikingfile on PS5** in the native app. This opens the provider page on the console.
3. Complete any verification yourself and select the provider’s **Download** button. Follow the file’s download controls if a redirect opens another Vikingfile page.
4. Return to Orbit Store and open **Downloads**. Orbit checks that the captured file matches the selected option before adding it to your queue.

![Vikingfile instructions inside Download options](../assets/0.9.0/desktop-viking.jpg)

*The Open download page on PS5 button starts the provider step. Download on Vikingfile comes next; then return to Orbit.*

You can start the session from a paired phone, but the provider page and verification still appear on the PS5. There is no need to paste a generated link. If the session expires or reports no matching file, return to Orbit and start that option again. Only one browser verification session can run at a time; **Cancel verification** stops the pending session without adding a download.

When a Vikingfile option offers **Download directly**, you can use that button to start it. Otherwise, follow the browser steps above.

<table>
  <tr><th>Choose an option on your phone</th><th>Start the PS5 browser step</th></tr>
  <tr>
    <td valign="top" width="50%"><img src="../assets/0.9.0/phone-details.jpg" width="280" alt="Phone game page with source and format options"></td>
    <td valign="top" width="50%"><img src="../assets/0.9.0/phone-viking.jpg" width="280" alt="Phone Vikingfile instructions and Open download page on PS5 button"></td>
  </tr>
</table>

*Interface previews use example storage and account data. Complete the Vikingfile download steps on your PS5.*

## Follow your queue

Use **Active**, **Finished**, **Failed**, and **Cancelled** to find a transfer. Move waiting items up or down, pause and resume, or cancel. Cancelled items have their own view; Finished contains successfully completed downloads.

![Native Downloads showing paused and queued sample transfers labelled via TorBox](../assets/0.9.0/native-downloads.png)

<p><a href="../assets/0.9.0/phone-downloads.jpg"><img src="../assets/0.9.0/phone-downloads.jpg" width="320" alt="Phone Downloads showing the same sample TorBox queue"></a></p>

*The TV app and paired phone show the same queue, illustrated here with sample paused and queued jobs.*

New supported large downloads use up to eight connections. Existing partials retain their original layout. Speed depends on the provider, network and drive. Pause, Resume and Cancel control the whole file.

After deleting a cancelled partial, you can start the download again from its game page. If you kept the partial, resume it from Downloads.

**Remove from history** and the history-clear buttons keep completed files. To remove a cancelled download and its partial file, use **Delete download** and confirm. If its drive is disconnected, reconnect it before deleting the file. If you already deleted the partial yourself, Orbit can clear the stale entry so you can start fresh.

Keep the PS5 awake. Closing the TV app or control browser leaves the download worker running; stopping Orbit interrupts it. Interrupted transfers return paused after restart. Orbit extracts supported archives after downloading. It does not directly install game packages, launch games or continue downloading in rest mode. For compatible drive files, see [Library](library.md).

## Get new games and corrected metadata

Orbit checks its catalogue on startup and every six hours. Use **App settings → Game catalogue → Refresh catalogue** for a manual check. You can browse the saved catalogue offline, and queued downloads keep the files you originally chose. New games and corrected release dates arrive without reinstalling Orbit, within the platforms supported by your app version. PS4 support itself requires the 1.1.0 app update.

[Getting started](getting-started.md) · [Troubleshooting](troubleshooting.md) · [Project home](../README.md)
