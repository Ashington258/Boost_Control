import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd

# 设置 Matplotlib 支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 读取 CSV 文件
df = pd.read_csv("test/data/U0_VADC.csv")  # ← 替换为你的路径

# 提取数据
v_out = df["UO"].to_numpy()
v_adc = df[df.columns[2]].to_numpy()  # 第三列为 VADC


# 线性拟合函数
def v_adc_linear(v_out, m, n):
    return m * v_out + n


# 二次拟合函数
def v_adc_quadratic(v_out, a, b, c):
    return a * v_out**2 + b * v_out + c


# 均方根误差
def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


# 线性拟合
popt_linear, _ = curve_fit(v_adc_linear, v_out, v_adc, p0=[0.1, 0])
m, n = popt_linear
v_adc_pred_linear = v_adc_linear(v_out, *popt_linear)
rmse_linear = rmse(v_adc, v_adc_pred_linear)

# 二次拟合
popt_quadratic, _ = curve_fit(v_adc_quadratic, v_out, v_adc, p0=[0, 0.1, 0])
a, b, c = popt_quadratic
v_adc_pred_quadratic = v_adc_quadratic(v_out, *popt_quadratic)
rmse_quadratic = rmse(v_adc, v_adc_pred_quadratic)

# 输出拟合参数与误差
print(f"线性拟合参数: m={m:.4f}, n={n:.4f}")
print(f"线性拟合 RMSE: {rmse_linear:.4f} V")
print(f"二次拟合参数: a={a:.6f}, b={b:.4f}, c={c:.4f}")
print(f"二次拟合 RMSE: {rmse_quadratic:.4f} V")

# 平滑曲线绘图
v_out_smooth = np.linspace(min(v_out), max(v_out), 100)
v_adc_pred_linear_smooth = v_adc_linear(v_out_smooth, *popt_linear)
v_adc_pred_quadratic_smooth = v_adc_quadratic(v_out_smooth, *popt_quadratic)

# 特定点估算
v_out_points = [30.0, 40.0]
v_adc_linear_30 = v_adc_linear(30.0, *popt_linear)
v_adc_linear_40 = v_adc_linear(40.0, *popt_linear)
v_adc_quadratic_30 = v_adc_quadratic(30.0, *popt_quadratic)
v_adc_quadratic_40 = v_adc_quadratic(40.0, *popt_quadratic)

print("\n交点 ADC 电压值（线性拟合）:")
print(f"V_out = 30V: V_adc = {v_adc_linear_30:.3f} V")
print(f"V_out = 40V: V_adc = {v_adc_linear_40:.3f} V")
print("\n交点 ADC 电压值（二次拟合）:")
print(f"V_out = 30V: V_adc = {v_adc_quadratic_30:.3f} V")
print(f"V_out = 40V: V_adc = {v_adc_quadratic_40:.3f} V")

# 绘图
plt.figure(figsize=(8, 6))
plt.scatter(v_out, v_adc, color="blue", label="测量数据")
plt.plot(
    v_out_smooth,
    v_adc_pred_linear_smooth,
    color="red",
    label=f"线性拟合: V_adc = {m:.4f}V_out + {n:.4f}\nRMSE={rmse_linear:.4f} V",
)
plt.plot(
    v_out_smooth,
    v_adc_pred_quadratic_smooth,
    color="green",
    label=f"二次拟合: V_adc = {a:.6f}V_out² + {b:.4f}V_out + {c:.4f}\nRMSE={rmse_quadratic:.4f} V",
)

plt.scatter(
    [30.0, 40.0],
    [v_adc_quadratic_30, v_adc_quadratic_40],
    color="purple",
    s=100,
    marker="x",
    label="交点 (二次拟合)",
)
plt.axvline(x=30.0, color="gray", linestyle="--", alpha=0.5)
plt.axvline(x=40.0, color="gray", linestyle="--", alpha=0.5)
plt.text(
    30.0,
    v_adc_quadratic_30 + 0.2,
    f"(30, {v_adc_quadratic_30:.3f})",
    color="purple",
    fontsize=10,
)
plt.text(
    40.0,
    v_adc_quadratic_40 + 0.2,
    f"(40, {v_adc_quadratic_40:.3f})",
    color="purple",
    fontsize=10,
)

plt.xlabel("输出电压 (V)")
plt.ylabel("ADC 电压 (V)")
plt.title("ADC 电压与输出电压关系")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# 预测全裕度点
v_out_low = max(v_out)  # 对应低占空比
v_out_high = min(v_out)  # 对应高占空比
v_adc_low_linear = v_adc_linear(v_out_low, *popt_linear)
v_adc_high_linear = v_adc_linear(v_out_high, *popt_linear)
v_adc_low_quadratic = v_adc_quadratic(v_out_low, *popt_quadratic)
v_adc_high_quadratic = v_adc_quadratic(v_out_high, *popt_quadratic)

print("\n全裕度预测结果（线性拟合）:")
print(f"输出电压 {v_out_low:.1f} V 时: ADC 电压 = {v_adc_low_linear:.3f} V")
print(f"输出电压 {v_out_high:.1f} V 时: ADC 电压 = {v_adc_high_linear:.3f} V")
print("\n全裕度预测结果（二次拟合）:")
print(f"输出电压 {v_out_low:.1f} V 时: ADC 电压 = {v_adc_low_quadratic:.3f} V")
print(f"输出电压 {v_out_high:.1f} V 时: ADC 电压 = {v_adc_high_quadratic:.3f} V")
