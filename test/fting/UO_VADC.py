import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 设置 Matplotlib 支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ================== 从 CSV 读取数据 ==================
# 文件路径（请根据实际路径修改）
csv_file = "test/data/U0_VADC.csv"

# 读取数据
df = pd.read_csv(csv_file)

# 提取数据列
UO = df["UO"].to_numpy()
VADC = df[df.columns[2]].to_numpy()  # 第三列通常是 VADC


# ========== 拟合函数定义 ==========
def linear_model(x, a, b):
    return a * x + b


def nonlinear_model(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


# ========== 线性拟合：UO → VADC ==========
popt_lin, _ = curve_fit(linear_model, UO, VADC)
vadc_lin_pred = linear_model(UO, *popt_lin)
rmse_lin = rmse(VADC, vadc_lin_pred)

# ========== 非线性拟合：UO → VADC ==========
popt_nonlin, _ = curve_fit(nonlinear_model, UO, VADC)
vadc_nonlin_pred = nonlinear_model(UO, *popt_nonlin)
rmse_nonlin = rmse(VADC, vadc_nonlin_pred)

# ========== 逆拟合（非线性）：VADC → UO ==========
popt_rev, _ = curve_fit(nonlinear_model, VADC, UO)
uo_rev_pred = nonlinear_model(VADC, *popt_rev)
rmse_rev = rmse(UO, uo_rev_pred)

# ========== 绘图 ==========
x_smooth = np.linspace(min(UO), max(UO), 200)
vadc_lin_smooth = linear_model(x_smooth, *popt_lin)
vadc_nonlin_smooth = nonlinear_model(x_smooth, *popt_nonlin)

plt.figure(figsize=(10, 5))
plt.scatter(UO, VADC, label="原始数据", color="blue")
plt.plot(
    x_smooth, vadc_lin_smooth, label=f"线性拟合\nRMSE={rmse_lin:.4f}", color="green"
)
plt.plot(
    x_smooth,
    vadc_nonlin_smooth,
    label=f"非线性拟合\nRMSE={rmse_nonlin:.4f}",
    color="red",
)
plt.xlabel("输出电压 UO (V)")
plt.ylabel("ADC 电压 VADC (V)")
plt.title("VADC vs UO 拟合")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ========== 逆拟合图 ==========
x_rev = np.linspace(min(VADC), max(VADC), 200)
uo_rev_smooth = nonlinear_model(x_rev, *popt_rev)

plt.figure()
plt.scatter(VADC, UO, color="blue", label="原始数据")
plt.plot(
    x_rev, uo_rev_smooth, color="orange", label=f"VADC→UO 逆拟合\nRMSE={rmse_rev:.4f}"
)
plt.xlabel("ADC 电压 VADC (V)")
plt.ylabel("输出电压 UO (V)")
plt.title("UO vs VADC 逆拟合")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ========== 打印拟合公式 ==========
print("\n🔎 线性拟合公式: VADC = a * UO + b")
print(f"→ VADC = {popt_lin[0]:.4f} * UO + {popt_lin[1]:.4f}")
print(f"RMSE: {rmse_lin:.4f} V")

print("\n🔎 非线性拟合公式: VADC = a * UO^3 + b * UO^2 + c * UO + d")
a, b, c, d = popt_nonlin
print(f"→ VADC = {a:.6f} * UO³ + {b:.6f} * UO² + {c:.6f} * UO + {d:.6f}")
print(f"RMSE: {rmse_nonlin:.4f} V")

print("\n🔁 逆拟合公式（VADC → UO）:")
a_r, b_r, c_r, d_r = popt_rev
print(f"→ UO = {a_r:.6f} * V³ + {b_r:.6f} * V² + {c_r:.6f} * V + {d_r:.6f}")
print(f"RMSE: {rmse_rev:.4f} V")
