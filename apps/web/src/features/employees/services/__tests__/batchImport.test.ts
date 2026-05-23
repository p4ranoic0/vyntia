import { describe, expect, it, vi, beforeEach } from "vitest";

vi.mock("@/shared/api/api", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

import { apiClient } from "@/shared/api/api";
import { employeesService } from "../employeesService";

function csvFile() {
  return new File(["numero_documento\n44556677\n"], "empleados.csv", {
    type: "text/csv",
  });
}

describe("employeesService.batchImport", () => {
  beforeEach(() => vi.resetAllMocks());

  it("POSTs multipart FormData to /api/v1/employees/batch-import/", async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { created: 2, errors: [] } },
    } as never);

    const result = await employeesService.batchImport(csvFile());

    const call = vi.mocked(apiClient.post).mock.calls[0];
    expect(call?.[0]).toBe("/api/v1/employees/batch-import/");
    expect(call?.[1]).toBeInstanceOf(FormData);
    expect((call?.[1] as FormData).get("file")).toBeInstanceOf(File);
    expect(result).toEqual({ created: 2, errors: [] });
  });

  it("normalizes a 422 rejection into the { created, errors } report", async () => {
    const report = {
      created: 0,
      errors: [{ row: 2, errors: { numero_documento: ["DNI inválido."] } }],
    };
    vi.mocked(apiClient.post).mockRejectedValueOnce({
      response: { status: 422, data: { errors: report } },
    });

    const result = await employeesService.batchImport(csvFile());

    expect(result.created).toBe(0);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0]?.row).toBe(2);
  });

  it("rethrows non-422 errors", async () => {
    vi.mocked(apiClient.post).mockRejectedValueOnce({
      response: { status: 500, data: { message: "boom" } },
    });

    await expect(employeesService.batchImport(csvFile())).rejects.toThrow();
  });
});
