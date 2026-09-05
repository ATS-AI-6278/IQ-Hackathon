import { Router, type IRouter } from "express";
import { ListActivityResponse } from "@workspace/api-zod";
import { listActivity } from "../lib/passport-store";

const router: IRouter = Router();

router.get("/activity", (_req, res): void => {
  res.json(ListActivityResponse.parse(listActivity()));
});

export default router;