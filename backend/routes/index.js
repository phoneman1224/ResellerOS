import { Router } from 'express';
import inventoryRoutes from './inventoryRoutes.js';
import listingRoutes from './listingRoutes.js';
import lotRoutes from './lotRoutes.js';
import expenseRoutes from './expenseRoutes.js';
import saleRoutes from './saleRoutes.js';
import settingsRoutes from './settingsRoutes.js';
import researchRoutes from './researchRoutes.js';

const router = Router();

router.use('/inventory', inventoryRoutes);
router.use('/listings', listingRoutes);
router.use('/lots', lotRoutes);
router.use('/expenses', expenseRoutes);
router.use('/sales', saleRoutes);
router.use('/settings', settingsRoutes);
router.use('/research', researchRoutes);

export default router;
