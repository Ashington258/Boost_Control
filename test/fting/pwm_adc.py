import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 设置 Matplotlib 支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
# 读取 CSV 数据
df = pd.read_csv("test/data/U0_VADC.csv")

# 提取并处理数据
duty = df["Duty"].str.rstrip("%").astype(float).to_numpy() / 100.0  # 转为小数
vadc = df[df.columns[2]].astype(float).to_numpy()  # 第三列是 VADC


# ---------- 拟合函数 ----------
def linear_model(x, a, b):
    return a * x + b


def nonlinear_model(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


# ---------- 正向拟合：Duty → VADC ----------
# 线性拟合
popt_lin, _ = curve_fit(linear_model, duty, vadc)
vadc_lin = linear_model(duty, *popt_lin)
rmse_lin = rmse(vadc, vadc_lin)

# 非线性拟合
popt_nonlin, _ = curve_fit(nonlinear_model, duty, vadc)
vadc_nonlin = nonlinear_model(duty, *popt_nonlin)
rmse_nonlin = rmse(vadc, vadc_nonlin)

# ---------- 逆向拟合：VADC → Duty ----------
popt_rev, _ = curve_fit(nonlinear_model, vadc, duty)
duty_rev = nonlinear_model(vadc, *popt_rev)
rmse_rev = rmse(duty, duty_rev)

# ---------- 绘图 ----------
duty_smooth = np.linspace(min(duty), max(duty), 200)
vadc_lin_smooth = linear_model(duty_smooth, *popt_lin)
vadc_nonlin_smooth = nonlinear_model(duty_smooth, *popt_nonlin)

plt.figure(figsize=(10, 5))
plt.scatter(duty * 100, vadc, label="原始数据", color="blue")
plt.plot(
    duty_smooth * 100,
    vadc_lin_smooth,
    color="green",
    label=f"线性拟合\nRMSE={rmse_lin:.4f}",
)
plt.plot(
    duty_smooth * 100,
    vadc_nonlin_smooth,
    color="red",
    label=f"非线性拟合\nRMSE={rmse_nonlin:.4f}",
)
plt.xlabel("占空比 Duty (%)")
plt.ylabel("ADC 电压 VADC (V)")
plt.title("VADC vs Duty 拟合")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ---------- 逆向拟合图 ----------
vadc_smooth = np.linspace(min(vadc), max(vadc), 200)
duty_pred_smooth = nonlinear_model(vadc_smooth, *popt_rev)

plt.figure()
plt.scatter(vadc, duty * 100, color="blue", label="原始数据")
plt.plot(
    vadc_smooth,
    duty_pred_smooth * 100,
    color="orange",
    label=f"逆向拟合\nRMSE={rmse_rev:.4f}",
)
plt.xlabel("ADC 电压 VADC (V)")
plt.ylabel("占空比 Duty (%)")
plt.title("Duty vs VADC 逆向拟合")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ---------- 打印拟合公式 ----------
print("\n🔎 线性拟合: VADC = a * D + b")
print(f"→ VADC = {popt_lin[0]:.6f} * D + {popt_lin[1]:.6f}")
print(f"RMSE: {rmse_lin:.4f} V")

print("\n🔎 非线性拟合: VADC = a * D^3 + b * D^2 + c * D + d")
a, b, c, d = popt_nonlin
print(f"→ VADC = {a:.6f}*D³ + {b:.6f}*D² + {c:.6f}*D + {d:.6f}")
print(f"RMSE: {rmse_nonlin:.4f} V")

print("\n🔁 逆向拟合: Duty = a * V^3 + b * V^2 + c * V + d")
a_r, b_r, c_r, d_r = popt_rev
print(f"→ Duty = {a_r:.6f}*V³ + {b_r:.6f}*V² + {c_r:.6f}*V + {d_r:.6f}")
print(f"RMSE: {rmse_rev:.4f}")
