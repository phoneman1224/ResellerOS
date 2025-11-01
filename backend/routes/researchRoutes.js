import { Router } from 'express';
import { researchController } from '../controllers/researchController.js';

const router = Router();

router.get('/', researchController.index);
router.get('/:id', researchController.show);
router.post('/', researchController.create);
router.put('/:id', researchController.update);
router.delete('/:id', researchController.destroy);

export default router;
