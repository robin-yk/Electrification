import { solveModel } from './solver.js';
self.onmessage = event => {
  try { self.postMessage({done: solveModel(event.data, progress => self.postMessage({progress}))}); }
  catch (error) { self.postMessage({error: error.message}); }
};

