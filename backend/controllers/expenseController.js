import {
  listExpenses,
  getExpense,
  createExpense,
  updateExpense,
  deleteExpense
} from '../models/expenseModel.js';

export const expenseController = {
  index: (_req, res) => {
    res.json(listExpenses());
  },
  show: (req, res) => {
    const expense = getExpense(Number(req.params.id));
    if (!expense) return res.status(404).json({ message: 'Expense not found' });
    res.json(expense);
  },
  create: (req, res) => {
    res.status(201).json(createExpense(req.body));
  },
  update: (req, res) => {
    const id = Number(req.params.id);
    const expense = getExpense(id);
    if (!expense) return res.status(404).json({ message: 'Expense not found' });
    res.json(updateExpense(id, req.body));
  },
  destroy: (req, res) => {
    const id = Number(req.params.id);
    const expense = getExpense(id);
    if (!expense) return res.status(404).json({ message: 'Expense not found' });
    deleteExpense(id);
    res.status(204).end();
  }
};
