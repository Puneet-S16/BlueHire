import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { getHealth } from "@/services/api";

const API_URL = "http://localhost:8000/api/v1";

describe("api.getHealth", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns health data on success", async () => {
    const mockFetch = globalThis.fetch as ReturnType<typeof vi.fn>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: "ok" }),
    } as Response);

    const result = await getHealth();

    expect(mockFetch).toHaveBeenCalledTimes(1);
    expect(mockFetch).toHaveBeenCalledWith(`${API_URL}/health`);
    expect(result).toEqual({ status: "ok" });
  });

  it("throws when response is not ok", async () => {
    const mockFetch = globalThis.fetch as ReturnType<typeof vi.fn>;
    mockFetch.mockResolvedValueOnce({
      ok: false,
    } as Response);

    await expect(getHealth()).rejects.toThrow("Network response was not ok");
  });
});
