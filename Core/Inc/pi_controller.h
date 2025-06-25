#ifndef PI_CONTROLLER_H
#define PI_CONTROLLER_H

typedef struct
{
    float kp;         // 比例系数
    float ki;         // 积分系数
    float dt;         // 控制周期（秒）
    float integral;   // 积分项
    float output_min; // 输出下限
    float output_max; // 输出上限
} PIController;

void PIController_Init(PIController *ctrl, float kp, float ki, float dt, float out_min, float out_max);
float PIController_Update(PIController *ctrl, float setpoint, float measurement);

extern float error;
#endif // PI_CONTROLLER_H
