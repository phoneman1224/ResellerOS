import { Router } from 'express';
import { settingsController } from '../controllers/settingsController.js';

const router = Router();

router.get('/', settingsController.show);
router.put('/', settingsController.update);

export default router;
