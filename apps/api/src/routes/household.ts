import { Router, type IRouter } from "express";
import { getPassport } from "../lib/passport-store";
import {
  compactGraphForAsk,
  graphNode,
  householdGraph,
  listRooms,
  noteProduct,
  placeProduct,
  quietNotices,
} from "../lib/household-graph";
import { runHouseholdAsk } from "../lib/ai-client";

const router: IRouter = Router();

router.post("/ask", async (req, res): Promise<void> => {
  const question = String(req.body?.question || "").trim();
  if (!question) {
    res.status(400).json({ error: "question is required" });
    return;
  }
  const result = await runHouseholdAsk(question, compactGraphForAsk());
  res.json(result);
});

router.get("/insights", (_req, res): void => {
  try {
    const notices = quietNotices();
    const graph = householdGraph();
    res.json({
      urgent: notices.filter((item) => item.kind === "warranty").map((item) => ({
        passportId: item.passportId,
        product: item.title,
        daysLeft: null,
        detail: item.detail,
      })),
      notices,
      rooms: graph.rooms.length,
      remembered: graph.nodes.length,
      pending: graph.nodes.filter((node) => node.missing.length > 0).length,
      healthyCount: graph.nodes.filter((node) => node.missing.length === 0).length,
      activeWarranties: graph.nodes.filter((node) => node.warrantyDaysLeft !== null && node.warrantyDaysLeft >= 0).length,
    });
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

router.get("/graph", (_req, res): void => {
  try {
    res.json(householdGraph());
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

router.get("/notices", (_req, res): void => {
  try {
    res.json({ notices: quietNotices() });
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

router.get("/rooms", (_req, res): void => {
  res.json({ rooms: listRooms() });
});

router.get("/product/:passportId", (req, res): void => {
  const passport = getPassport(String(req.params.passportId));
  if (!passport) {
    res.status(404).json({ error: "Not remembered yet" });
    return;
  }
  res.json(graphNode(passport));
});

router.post("/product/:passportId/place", (req, res): void => {
  const memory = placeProduct(
    String(req.params.passportId),
    req.body?.roomId || null,
    req.body?.locationNote,
    req.body?.confidence || "confirmed",
  );
  if (!memory) {
    res.status(404).json({ error: "Not remembered yet" });
    return;
  }
  const passport = getPassport(memory.passportId);
  res.json(passport ? graphNode(passport) : memory);
});

router.post("/product/:passportId/note", (req, res): void => {
  const memory = noteProduct(String(req.params.passportId), String(req.body?.notes || ""));
  if (!memory) {
    res.status(404).json({ error: "Not remembered yet" });
    return;
  }
  res.json(memory);
});

export default router;
