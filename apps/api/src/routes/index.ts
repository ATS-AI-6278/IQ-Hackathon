import { Router, type IRouter } from "express";
import healthRouter from "./health";
import passportsRouter from "./passports";
import productsRouter from "./products";
import activityRouter from "./activity";
import systemRouter from "./system";
import demoRouter from "./demo";

const router: IRouter = Router();

router.use(healthRouter);
router.use(passportsRouter);
router.use(productsRouter);
router.use(activityRouter);
router.use(systemRouter);
router.use(demoRouter);

export default router;
