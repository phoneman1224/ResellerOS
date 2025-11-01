import { Router } from 'express';
import { inventoryController } from '../controllers/inventoryController.js';

const router = Router();

router.get('/', inventoryController.index);
router.get('/:id', inventoryController.show);
router.post('/', inventoryController.create);
router.put('/:id', inventoryController.update);
router.delete('/:id', inventoryController.destroy);

export default router;
