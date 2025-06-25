import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd

# 设置 Matplotlib 支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 读取 CSV 文件
df = pd.read_csv("test/data/U0_VADC.csv")  # ← 替换为你的路径

# 数据预处理
duty_cycle = df["Duty"].str.rstrip("%").astype(float).to_numpy() / 100
v_adc = df[df.columns[2]].to_numpy()  # 第三列是 ADC 电压


# 定义线性拟合函数：D = a * V_adc + b
def duty_linear_fit(vadc, a, b):
    return a * vadc + b


# 拟合
popt_linear, _ = curve_fit(duty_linear_fit, v_adc, duty_cycle, p0=[0.1, 0])
a_lin, b_lin = popt_linear


# 预测 & 误差
def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


duty_pred = duty_linear_fit(v_adc, *popt_linear)
rmse_linear = rmse(duty_cycle, duty_pred)

# 绘图
vadc_smooth = np.linspace(min(v_adc), max(v_adc), 200)
duty_smooth = duty_linear_fit(vadc_smooth, *popt_linear)

plt.figure(figsize=(8, 5))
plt.scatter(v_adc, duty_cycle * 100, color="blue", label="测量数据")
plt.plot(
    vadc_smooth,
    duty_smooth * 100,
    color="red",
    label=f"拟合: D = {a_lin:.4f} * V + {b_lin:.4f}\nRMSE = {rmse_linear:.4f}",
)
plt.xlabel("ADC 电压 (V)")
plt.ylabel("占空比 (%)")
plt.title("占空比与 ADC 电压（线性拟合）")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# 打印拟合公式
print("\n线性逆拟合公式与误差：")
print(f"Duty 拟合公式: D = {a_lin:.6f} * V_adc + {b_lin:.6f}")
print(f"线性逆向拟合 RMSE: {rmse_linear:.6f}")
