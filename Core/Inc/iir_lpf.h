/* iir_lpf.h */
#ifndef __IIR_LPF_H
#define __IIR_LPF_H

#include <stdint.h>
#include "main.h"
/**
 * @brief 一阶 IIR 低通滤波器句柄
 */
typedef struct
{
    float alpha;    /**< 滤波系数 α，范围 0.0f~1.0f */
    float prev_out; /**< 上一次滤波输出 */
} IIR_LPF_HandleTypeDef;

/**
 * @brief 初始化 IIR 一阶低通滤波器
 * @param h     过滤器句柄指针
 * @param alpha 滤波系数 α（越接近 1，平滑效果越强，响应越慢）
 * @param init  初始输出值（通常可设为第一帧采样）
 */
void IIR_LPF_Init(IIR_LPF_HandleTypeDef *h, float alpha, float init);

/**
 * @brief 对单个新采样执行滤波
 * @param h      过滤器句柄指针
 * @param sample 新采样值
 * @return       本次滤波后的输出
 */
float IIR_LPF_Update(IIR_LPF_HandleTypeDef *h, float sample);

#endif /* __IIR_LPF_H */
