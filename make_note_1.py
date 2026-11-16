import os
papers = [
    {
        "idx": 0, "id": "2610.02207", "date": "2026-10-01",
        "title_en": "One Basis to Animate Them All: Gaussian Blendshape Distillation for Real-Time Avatars",
        "title_zh": "一個基底動畫全部：高斯混合塑型蒸餾用於即時虛擬化身",
        "authors": ["Ramazan Fazylov", "Stamatis Lefkimmiatis", "Ivan Laptev"],
    },
    {
        "idx": 1, "id": "2610.02206", "date": "2026-10-01",
        "title_en": "KaliBench: A Fine-Grained Benchmark for Cybersecurity Tool Use on Kali Linux with Runtime-Free Verifiable Rewards",
        "title_zh": "KaliBench：基於 Kali Linux 的細粒度資安工具使用基準，附無運行時可驗證獎勵",
        "authors": ["Pengfei Li", "Naufal Suryanto", "Sicheng Zhang"],
    },
    {
        "idx": 2, "id": "2610.02204", "date": "2026-10-01",
        "title_en": "Reconstruct, Practice, Go Real: Guided Self-Improvement for Embodied Agents",
        "title_zh": "重建、練習、上場：具身代理的引導式自我改進",
        "authors": ["Yen-Jen Wang", "Haozhe Jiang", "Shuying Deng"],
    },
    {
        "idx": 3, "id": "2610.02202", "date": "2026-10-01",
        "title_en": "ScholarCatalyst: A Benchmark for Retrieving Papers That Inspire New Research",
        "title_zh": "ScholarCatalyst：激發新研究的論文檢索基準",
        "authors": ["Sohyeon Kim", "Yoonho Lee", "Bo Liu"],
    },
    {
        "idx": 4, "id": "2610.02201", "date": "2026-10-01",
        "title_en": "SILSA: Sliding-Window Slice Latents for Topology-Preserving High-Resolution 3D Generation",
        "title_zh": "SILSA：滑動視窗切片潛變數以保持拓樸的高分辨率 3D 生成",
        "authors": ["Tianjiao Yu", "Xinzhuo Li", "Yifan Shen"],
    },
    {
        "idx": 5, "id": "2610.02200", "date": "2026-10-01",
        "title_en": "VISTA: A Visual Harness for Reasoning in an Interactive World",
        "title_zh": "VISTA：互動世界推理的視覺整合框架",
        "authors": ["Qiushi Han", "Keya Hu", "Linlu Qiu"],
    },
    {
        "idx": 6, "id": "2610.02198", "date": "2026-10-01",
        "title_en": "FERPO: Forward Entropy-Regularized Policy Optimization",
        "title_zh": "FERPO：前向熵正則化策略最佳化",
        "authors": ["Sebastian Sanokowski", "Alireza Sarmadi", "Majid Khadiv"],
    },
    {
        "idx": 7, "id": "2610.02193", "date": "2026-10-01",
        "title_en": "Hierarchical Continuous Diffusion Language Models",
        "title_zh": "階層式連續擴散語言模型",
        "authors": ["Hui Ren", "Zihan Li", "Chang Liu"],
    },
    {
        "idx": 8, "id": "2610.02188", "date": "2026-10-01",
        "title_en": "DMAD: Distribution Matching as Adversarial Distillation for Fast Visual Generation",
        "title_zh": "DMAD：以分布匹配作為對抗蒸餾加速視覺生成",
        "authors": ["Zhengming Yu", "Junkun Yuan", "Haotian Yang"],
    },
    {
        "idx": 9, "id": "2610.02186", "date": "2026-10-01",
        "title_en": "Higher-Order Molecular Grammars for Generative and Foundation Models in Chemistry",
        "title_zh": "高階分子文法用於化學生成式與基礎模型",
        "authors": ["Yiming Huang", "Yujie Zeng", "Vijay Prakash Dwivedi"],
    },
]
print(len(papers))
