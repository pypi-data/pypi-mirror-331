from prepmagma import res
import matplotlib.pyplot as plt
plt.style.use("/mnt/data/hong/reference/general.mplstyle")
df = res.compile_res('gsea/include', 'gsea/summary.txt', 'common')
res.heatmap(df, 'gsea/heatmap_common.pdf')