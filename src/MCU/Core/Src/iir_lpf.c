/* iir_lpf.c */
#include "iir_lpf.h"

void IIR_LPF_Init(IIR_LPF_HandleTypeDef *h, float alpha, float init)
{
    if (alpha < 0.0f)
        alpha = 0.0f;
    if (alpha > 1.0f)
        alpha = 1.0f;
    h->alpha = alpha;
    h->prev_out = init;
}

float IIR_LPF_Update(IIR_LPF_HandleTypeDef *h, float sample)
{
    // y[n] = α⋅y[n-1] + (1-α)⋅x[n]
    h->prev_out = h->alpha * h->prev_out + (1.0f - h->alpha) * sample;
    return h->prev_out;
}
