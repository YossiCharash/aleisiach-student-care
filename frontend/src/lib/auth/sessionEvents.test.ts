import { describe, expect, it, vi } from "vitest";
import { notifyUnauthorized, onUnauthorized } from "@/lib/auth/sessionEvents";

describe("session events", () => {
  it("invokes every registered handler on notify", () => {
    const first = vi.fn();
    const second = vi.fn();
    onUnauthorized(first);
    onUnauthorized(second);

    notifyUnauthorized();

    expect(first).toHaveBeenCalledTimes(1);
    expect(second).toHaveBeenCalledTimes(1);
  });

  it("stops invoking a handler after it unsubscribes", () => {
    const handler = vi.fn();
    const unsubscribe = onUnauthorized(handler);

    unsubscribe();
    notifyUnauthorized();

    expect(handler).not.toHaveBeenCalled();
  });
});
