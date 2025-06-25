import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 设置 Matplotlib 支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 使用 SimHei 字体
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 数据
duty_cycle = np.array([25, 30, 40, 50, 60, 70]) / 100  # 占空比 (0.25 to 0.70)
v_out = np.array([61.94, 53.436, 40.108, 32.822, 27.720, 23.959])  # 输出电压 (V)
v_adc = np.array([5.437, 4.741, 3.677, 2.991, 2.524, 2.175])  # ADC 电压 (V)


# 定义改进的 Boost 电路输出电压拟合函数
def v_out_fit(D, a, b, c):
    """
    改进模型: V_out = a / (1 - D) + b + c * D
    a: 接近输入电压 V_in
    b: 固定偏移（如二极管压降）
    c: 线性损耗项（考虑电感电阻等）
    """
    return a / (1 - D) + b + c * D


# 定义 ADC 电压的三次多项式拟合函数
def v_adc_fit(D, a, b, c, d):
    """
    三次多项式: V_adc = a * D^3 + b * D^2 + c * D + d
    """
    return a * D**3 + b * D**2 + c * D + d


# 计算均方根误差 (RMSE)
def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


# 拟合输出电压
popt_v_out, _ = curve_fit(v_out_fit, duty_cycle, v_out, p0=[18, -1, 0])
a, b, c = popt_v_out
v_out_pred_data = v_out_fit(duty_cycle, *popt_v_out)
rmse_v_out = rmse(v_out, v_out_pred_data)
print(f"输出电压拟合参数: a={a:.3f}, b={b:.3f}, c={c:.3f}")
print(f"输出电压 RMSE: {rmse_v_out:.3f} V")

# 拟合 ADC 电压
popt_v_adc, _ = curve_fit(v_adc_fit, duty_cycle, v_adc, p0=[0, 0, 0, 5])
a_adc, b_adc, c_adc, d_adc = popt_v_adc
v_adc_pred_data = v_adc_fit(duty_cycle, *popt_v_adc)
rmse_v_adc = rmse(v_adc, v_adc_pred_data)
print(f"ADC 电压拟合参数: a={a_adc:.3f}, b={b_adc:.3f}, c={c_adc:.3f}, d={d_adc:.3f}")
print(f"ADC 电压 RMSE: {rmse_v_adc:.3f} V")

# 生成平滑曲线用于绘图和预测
D_smooth = np.linspace(0.15, 0.85, 100)  # 占空比从 15% 到 85%（避免极端外推）
v_out_pred = v_out_fit(D_smooth, *popt_v_out)
v_adc_pred = v_adc_fit(D_smooth, *popt_v_adc)

# 绘制曲线
plt.figure(figsize=(12, 5))

# 子图1：输出电压 vs 占空比
plt.subplot(1, 2, 1)
plt.scatter(duty_cycle * 100, v_out, color="blue", label="测量数据")
plt.plot(
    D_smooth * 100,
    v_out_pred,
    color="red",
    label=f"拟合曲线: V_out = {a:.2f}/(1-D) + {b:.2f} + {c:.2f}D\nRMSE={rmse_v_out:.3f} V",
)
plt.xlabel("占空比 (%)")
plt.ylabel("输出电压 (V)")
plt.title("输出电压与占空比关系")
plt.grid(True)
plt.legend()

# 子图2：ADC 电压 vs 占空比
plt.subplot(1, 2, 2)
plt.scatter(duty_cycle * 100, v_adc, color="blue", label="测量数据")
plt.plot(
    D_smooth * 100,
    v_adc_pred,
    color="red",
    label=f"拟合曲线: V_adc = {a_adc:.2f}D³ + {b_adc:.2f}D² + {c_adc:.2f}D + {d_adc:.2f}\nRMSE={rmse_v_adc:.3f} V",
)
plt.xlabel("占空比 (%)")
plt.ylabel("ADC 电压 (V)")
plt.title("ADC 电压与占空比关系")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

# 预测全裕度数值
D_low = 0.15  # 15%
D_high = 0.85  # 85%
v_out_low = v_out_fit(D_low, *popt_v_out)
v_out_high = v_out_fit(D_high, *popt_v_out)
v_adc_low = v_adc_fit(D_low, *popt_v_adc)
v_adc_high = v_adc_fit(D_high, *popt_v_adc)

print("\n全裕度预测结果:")
print(f"占空比 15% 时: 输出电压 = {v_out_low:.3f} V, ADC 电压 = {v_adc_low:.3f} V")
print(f"占空比 85% 时: 输出电压 = {v_out_high:.3f} V, ADC 电压 = {v_adc_high:.3f} V")
