#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
重置API数据脚本
"""

import os
import json
import sys

def main():
    print("开始重置预测数据...")
    # 构建默认预测数据
    predictions = {
        "科技": [
            {
                "title": "华为发布新一代鸿蒙OS，性能提升50%",
                "reason": "随着华为在国内市场的持续复苏，新一代操作系统的发布将引起广泛关注。该系统预计将带来显著的性能提升和更多自主创新功能，有望进一步巩固华为在国内智能设备生态系统的地位。"
            },
            {
                "title": "国内芯片制造取得重大突破，7nm工艺良率提高",
                "reason": "在全球半导体供应链调整的背景下，国内芯片制造能力的提升是热门话题。随着技术的进步和投资的增加，国产芯片制造工艺的突破将引发广泛讨论，对科技自主可控具有重要意义。"
            },
            {
                "title": "苹果智能眼镜推迟发布，技术难题尚未解决",
                "reason": "苹果一直在AR/VR领域布局，市场对其智能眼镜产品期待已久。如果出现推迟发布的消息，将引发对技术瓶颈和产品成熟度的讨论，同时影响相关供应链股票表现。"
            }
        ],
        "职场": [
            {
                "title": "大厂招聘回暖，AI岗位需求激增200%",
                "reason": "随着AI技术的快速发展和商业化应用的扩大，大型科技公司对AI人才的需求将继续增长。这一趋势反映了就业市场的结构性变化，也将引导更多年轻人转向AI相关专业学习。"
            },
            {
                "title": "远程办公新政出台，三成企业将采用混合工作模式",
                "reason": "疫情后，远程和混合办公模式已成为新常态。政府和企业可能出台新的政策来规范和支持这种工作方式，平衡效率和员工满意度，这将成为职场热议话题。"
            },
            {
                "title": "职场\"35岁现象\"引发社会关注，多地出台应对政策",
                "reason": "年龄歧视问题一直是职场热点话题，特别是科技行业的\"35岁危机\"。随着人口老龄化加速和退休年龄延长讨论，社会对中年职场人的关注度会提高，可能促使政策调整和企业文化变革。"
            }
        ],
        "AI新闻": [
            {
                "title": "国产大模型新突破，理解能力首次超越GPT-4",
                "reason": "随着国内AI研发的持续投入，国产大模型在某些特定领域的能力有望取得突破。这类消息将引起广泛关注，因为它代表了中国在AI领域的竞争力提升，也将影响相关企业的市场估值。"
            },
            {
                "title": "首个AI生成内容版权保护法案出台，明确责任边界",
                "reason": "随着AI生成内容的普及，版权保护问题日益突出。相关法律法规的出台将是必然趋势，这将对创作者、平台和AI开发者产生重大影响，也将引发广泛的社会讨论。"
            },
            {
                "title": "多模态AI应用爆发式增长，图像识别准确率达99.8%",
                "reason": "随着AI技术的进步，特别是多模态模型的发展，AI在图像识别等领域的能力将继续提升。这些技术突破将加速AI在医疗、安防等行业的应用，引发新一轮的AI应用热潮。"
            }
        ]
    }

    # 写入数据
    try:
        data_dir = os.path.join(os.getcwd(), "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"创建数据目录: {data_dir}")
            
        predictions_file = os.path.join(data_dir, "predictions.json")
        with open(predictions_file, "w", encoding="utf-8") as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)
        print(f"成功写入预测数据到 {predictions_file}")
    except Exception as e:
        print(f"错误: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main()) 