import { describe, expect, it, vi } from "vitest";
import { blobToBase64, preferredRecordingMimeType } from "./audio";

describe("audio utils", () => {
  it("encodes a blob as base64", async () => {
    await expect(blobToBase64(new Blob(["voice"]))).resolves.toBe("dm9pY2U=");
  });

  it("selects the first supported MediaRecorder mime type", () => {
    class FakeMediaRecorder {
      static isTypeSupported(value: string) {
        return value === "audio/webm";
      }
    }
    vi.stubGlobal("MediaRecorder", FakeMediaRecorder);

    expect(preferredRecordingMimeType()).toBe("audio/webm");
  });
});
