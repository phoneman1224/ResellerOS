#!/usr/bin/env node
import db from '../backend/utils/database.js';

const inventory = db.prepare('INSERT INTO inventory_items (name, category, condition, cost, quantity, tags) VALUES (?, ?, ?, ?, ?, ?)');
const expenses = db.prepare('INSERT INTO expenses (name, amount, category, deductible, incurred_on) VALUES (?, ?, ?, ?, ?)');

inventory.run('Vintage Jacket', 'Clothing', 'Used - Excellent', 25, 1, JSON.stringify(['vintage', 'outerwear']));
inventory.run('Retro Console', 'Electronics', 'Tested', 45, 1, JSON.stringify(['gaming', 'retro']));
expenses.run('Shipping Supplies', 12.5, 'Supplies', 1, '2024-01-10');

console.log('Seed data inserted.');
