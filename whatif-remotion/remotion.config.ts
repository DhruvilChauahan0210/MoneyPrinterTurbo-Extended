import fs from "fs";
import { Config } from "@remotion/cli/config";
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// The Mac uses a local Playwright headless shell; elsewhere Remotion downloads its own browser.
const MAC_BROWSER =
  "/Users/dhruvilchauhan/Library/Caches/ms-playwright/chromium_headless_shell-1246/chrome-headless-shell-mac-arm64/chrome-headless-shell";
if (fs.existsSync(MAC_BROWSER)) {
  Config.setBrowserExecutable(MAC_BROWSER);
}
