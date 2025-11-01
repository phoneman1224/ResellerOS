import { Router } from 'express';
import { expenseController } from '../controllers/expenseController.js';

const router = Router();

router.get('/', expenseController.index);
router.get('/:id', expenseController.show);
router.post('/', expenseController.create);
router.put('/:id', expenseController.update);
router.delete('/:id', expenseController.destroy);

export default router;
