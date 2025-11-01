import { Router } from 'express';
import { lotController } from '../controllers/lotController.js';
import { aiService } from '../services/aiService.js';

const router = Router();

router.get('/', lotController.index);
router.get('/:id', lotController.show);
router.post('/', lotController.create);
router.put('/:id', lotController.update);
router.delete('/:id', lotController.destroy);

router.post('/seo', async (req, res) => {
  const completion = await aiService.generateListingSEO(req.body);
  res.json(completion);
});

export default router;
