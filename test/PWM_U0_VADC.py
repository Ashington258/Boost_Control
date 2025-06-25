import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd

# 设置 Matplotlib 支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 读取 CSV 文件
df = pd.read_csv("test/data/U0_VADC.csv")  # ← 替换为你的文件名或路径

# 数据预处理
duty_cycle = df["Duty"].str.rstrip("%").astype(float).to_numpy() / 100
v_out = df["UO"].to_numpy()
v_adc = df[df.columns[2]].to_numpy()  # 取第三列（ADC电压）


# 拟合函数
def v_out_fit(D, a, b, c):
    return a / (1 - D) + b + c * D


def v_adc_fit(D, a, b, c, d):
    return a * D**3 + b * D**2 + c * D + d


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


# 拟合输出电压
popt_v_out, _ = curve_fit(v_out_fit, duty_cycle, v_out, p0=[18, -1, 0])
a, b, c = popt_v_out
v_out_pred_data = v_out_fit(duty_cycle, *popt_v_out)
rmse_v_out = rmse(v_out, v_out_pred_data)

# 拟合 ADC 电压
popt_v_adc, _ = curve_fit(v_adc_fit, duty_cycle, v_adc, p0=[0, 0, 0, 5])
a_adc, b_adc, c_adc, d_adc = popt_v_adc
v_adc_pred_data = v_adc_fit(duty_cycle, *popt_v_adc)
rmse_v_adc = rmse(v_adc, v_adc_pred_data)

# 平滑曲线
D_smooth = np.linspace(0.35, 0.75, 200)
v_out_pred = v_out_fit(D_smooth, *popt_v_out)
v_adc_pred = v_adc_fit(D_smooth, *popt_v_adc)

# 绘图
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(duty_cycle * 100, v_out, color="blue", label="测量数据")
plt.plot(
    D_smooth * 100,
    v_out_pred,
    color="red",
    label=f"拟合: V_out = {a:.2f}/(1-D) + {b:.2f} + {c:.2f}D\nRMSE={rmse_v_out:.3f} V",
)
plt.xlabel("占空比 (%)")
plt.ylabel("输出电压 (V)")
plt.title("输出电压与占空比")
plt.grid(True)
plt.legend()

plt.subplot(1, 2, 2)
plt.scatter(duty_cycle * 100, v_adc, color="blue", label="测量数据")
plt.plot(
    D_smooth * 100,
    v_adc_pred,
    color="red",
    label=f"拟合: V_adc = {a_adc:.2f}D³ + {b_adc:.2f}D² + {c_adc:.2f}D + {d_adc:.2f}\nRMSE={rmse_v_adc:.3f} V",
)
plt.xlabel("占空比 (%)")
plt.ylabel("ADC 电压 (V)")
plt.title("ADC 电压与占空比")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

# 预测边界裕度值
D_low, D_high = 0.15, 0.85
v_out_low, v_out_high = v_out_fit(D_low, *popt_v_out), v_out_fit(D_high, *popt_v_out)
v_adc_low, v_adc_high = v_adc_fit(D_low, *popt_v_adc), v_adc_fit(D_high, *popt_v_adc)

print("\n全裕度预测结果:")
print(f"占空比 15% 时: 输出电压 = {v_out_low:.3f} V, ADC 电压 = {v_adc_low:.3f} V")
print(f"占空比 85% 时: 输出电压 = {v_out_high:.3f} V, ADC 电压 = {v_adc_high:.3f} V")


# 打印拟合关系
print("\n拟合公式与参数：")
print(f"输出电压拟合公式: V_out = {a:.4f}/(1 - D) + {b:.4f} + {c:.4f}*D")
print(f"输出电压 RMSE: {rmse_v_out:.4f} V")

print(
    f"\nADC 电压拟合公式: V_adc = {a_adc:.4f}*D³ + {b_adc:.4f}*D² + {c_adc:.4f}*D + {d_adc:.4f}"
)
print(f"ADC 电压 RMSE: {rmse_v_adc:.4f} V")


# 逆向拟合：V_ADC → Duty
def duty_fit(vadc, a, b, c, d):
    return a * vadc**3 + b * vadc**2 + c * vadc + d


# 用原始数据反向拟合
popt_duty, _ = curve_fit(duty_fit, v_adc, duty_cycle, p0=[0, 0, 0, 0])
a_duty, b_duty, c_duty, d_duty = popt_duty

# 计算预测与 RMSE
duty_pred = duty_fit(v_adc, *popt_duty)
rmse_duty = rmse(duty_cycle, duty_pred)

# 拟合曲线绘制
vadc_smooth = np.linspace(min(v_adc), max(v_adc), 200)
duty_smooth = duty_fit(vadc_smooth, *popt_duty)

plt.figure()
plt.scatter(v_adc, duty_cycle * 100, color="blue", label="测量数据")
plt.plot(
    vadc_smooth,
    duty_smooth * 100,
    color="red",
    label=f"拟合: D = {a_duty:.4f}*V³ + {b_duty:.4f}*V² + {c_duty:.4f}*V + {d_duty:.4f}\nRMSE={rmse_duty:.4f}",
)
plt.xlabel("ADC 电压 (V)")
plt.ylabel("占空比 (%)")
plt.title("占空比与 ADC 电压（逆拟合）")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# 打印逆拟合公式
print("\n逆拟合公式与误差：")
print(
    f"Duty 拟合公式: D = {a_duty:.4f}*V³ + {b_duty:.4f}*V² + {c_duty:.4f}*V + {d_duty:.4f}"
)
print(f"Duty 逆向拟合 RMSE: {rmse_duty:.4f}")
