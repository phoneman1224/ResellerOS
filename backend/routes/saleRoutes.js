import { Router } from 'express';
import { saleController } from '../controllers/saleController.js';

const router = Router();

router.get('/', saleController.index);
router.get('/:id', saleController.show);
router.post('/', saleController.create);
router.put('/:id', saleController.update);
router.delete('/:id', saleController.destroy);

export default router;
