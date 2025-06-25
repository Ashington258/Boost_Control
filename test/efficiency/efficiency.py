import pandas as pd
import matplotlib.pyplot as plt

# 设置 Matplotlib 支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
# 读取 CSV 文件
df = pd.read_csv("test/data/efficiency.csv")  # ← 替换为你的文件路径

# 提取输入功率 Pi 和输出功率 Po
Pi = df["Pi"]
Po = df["Po"]

# 计算效率 η（百分比）
df["Efficiency (%)"] = (Po / Pi) * 100

# 打印效率表格
print("功率效率数据：")
print(df)

# 绘图：效率 vs 输入功率
plt.figure(figsize=(8, 5))
plt.plot(
    Pi,
    df["Efficiency (%)"],
    marker="o",
    linestyle="-",
    color="green",
    label="Efficiency",
)

# 标注最大效率
max_eff_idx = df["Efficiency (%)"].idxmax()
max_pi = Pi[max_eff_idx]
max_eff = df["Efficiency (%)"][max_eff_idx]
plt.annotate(
    f"Max η = {max_eff:.2f}%",
    xy=(max_pi, max_eff),
    xytext=(max_pi + 2, max_eff - 3),
    arrowprops=dict(arrowstyle="->", color="red"),
    color="red",
)

# 设置图形属性
plt.xlabel("输入功率 Pi (W)")
plt.ylabel("效率 η (%)")
plt.title("电源效率曲线")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
