import {
  listInventory,
  getInventoryItem,
  createInventoryItem,
  updateInventoryItem,
  deleteInventoryItem
} from '../models/inventoryModel.js';

export const inventoryController = {
  index: (req, res) => {
    res.json(listInventory());
  },
  show: (req, res) => {
    const item = getInventoryItem(Number(req.params.id));
    if (!item) return res.status(404).json({ message: 'Inventory item not found' });
    res.json(item);
  },
  create: (req, res) => {
    const payload = req.body;
    res.status(201).json(createInventoryItem(payload));
  },
  update: (req, res) => {
    const id = Number(req.params.id);
    const existing = getInventoryItem(id);
    if (!existing) return res.status(404).json({ message: 'Inventory item not found' });
    res.json(updateInventoryItem(id, req.body));
  },
  destroy: (req, res) => {
    const id = Number(req.params.id);
    const existing = getInventoryItem(id);
    if (!existing) return res.status(404).json({ message: 'Inventory item not found' });
    deleteInventoryItem(id);
    res.status(204).end();
  }
};
