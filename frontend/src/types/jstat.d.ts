/**
 * Declaração de tipos para jstat
 * https://github.com/jstat/jstat
 */

declare module 'jstat' {
  interface JStatDistribution {
    /**
     * Cumulative Distribution Function
     * P(X <= x)
     */
    cdf(x: number, ...params: number[]): number;

    /**
     * Probability Density/Mass Function
     */
    pdf(x: number, ...params: number[]): number;

    /**
     * Inverse CDF (Quantile function)
     */
    inv(p: number, ...params: number[]): number;

    /**
     * Mean
     */
    mean(...params: number[]): number;

    /**
     * Variance
     */
    variance(...params: number[]): number;
  }

  interface JStatPoisson extends JStatDistribution {
    /**
     * P(X <= x) for Poisson distribution
     * @param x - value
     * @param lambda - rate parameter (λ > 0)
     */
    cdf(x: number, lambda: number): number;

    /**
     * P(X = x) for Poisson distribution
     * @param x - value
     * @param lambda - rate parameter (λ > 0)
     */
    pdf(x: number, lambda: number): number;
  }

  interface JStatNormal extends JStatDistribution {
    /**
     * P(X <= x) for Normal distribution
     * @param x - value
     * @param mean - mean (μ)
     * @param std - standard deviation (σ > 0)
     */
    cdf(x: number, mean: number, std: number): number;

    /**
     * f(x) for Normal distribution
     * @param x - value
     * @param mean - mean (μ)
     * @param std - standard deviation (σ > 0)
     */
    pdf(x: number, mean: number, std: number): number;
  }

  interface JStatStatic {
    poisson: JStatPoisson;
    normal: JStatNormal;
  }

  const jStat: JStatStatic;
  export = jStat;
}
