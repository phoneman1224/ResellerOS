import { Router } from 'express';
import { listingController } from '../controllers/listingController.js';
import { aiService } from '../services/aiService.js';

const router = Router();

router.get('/', listingController.index);
router.get('/:id', listingController.show);
router.post('/', listingController.create);
router.put('/:id', listingController.update);
router.delete('/:id', listingController.destroy);

router.post('/seo', async (req, res) => {
  const payload = req.body;
  const completion = await aiService.generateListingSEO(payload);
  res.json(completion);
});

router.post('/pricing', async (req, res) => {
  const payload = req.body;
  const completion = await aiService.generatePricingInsight(payload);
  res.json(completion);
});

export default router;
