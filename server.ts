import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Route for prediction
  app.post("/predict", (req, res) => {
    try {
      const data = req.body;
      
      // Basic mock model logic
      // In a real scenario, this would call a FastAPI backend or a local Python model.
      
      let churnProbability = 0.2; // Base probability
      
      if (data.contract === "Month-to-month") churnProbability += 0.3;
      if (data.internetService === "Fiber optic") churnProbability += 0.15;
      if (data.tenure < 12) churnProbability += 0.2;
      if (data.paymentMethod === "Electronic check") churnProbability += 0.1;
      if (data.seniorCitizen === "Yes") churnProbability += 0.05;
      
      if (data.techSupport === "Yes") churnProbability -= 0.1;
      if (data.onlineSecurity === "Yes") churnProbability -= 0.1;

      // Cap between 0.01 and 0.99
      churnProbability = Math.max(0.01, Math.min(0.99, churnProbability));
      
      // Random noise
      churnProbability += (Math.random() * 0.04) - 0.02;

      const prediction = churnProbability > 0.5 ? "Churn" : "No Churn";
      const confidenceScore = churnProbability > 0.5 ? churnProbability : 1 - churnProbability;

      // Simulate a bit of processing delay
      setTimeout(() => {
        res.json({
          prediction,
          probability: churnProbability,
          confidence_score: confidenceScore,
          timestamp: new Date().toISOString()
        });
      }, 800);
      
    } catch (error) {
      console.error(error);
      res.status(500).json({ error: "Prediction failed." });
    }
  });

  app.get("/api/health", (req, res) => {
    res.json({ status: "ok" });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
