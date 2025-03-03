import matplotlib
import numpy as np
matplotlib.use("TkAgg")  # todo
import matplotlib.pyplot as plt

models = ['claude-3-7-sonnet', 'deepseek-r1',  "o1-mini", 'gpt-4o-mini', 'o3-mini',]
recall_2 = [0.86, 0.78, 0.805, 0.76, 0.715, ]
recall_5 = [0.91, 0.89, 0.865, 0.795, 0.745, ]

# 设置柱状图的位置和宽度
bar_width = 0.35
index = np.arange(len(models))


# plt.figure(figsize=(10, 6))
fig, ax = plt.subplots(figsize=(8, 6))

# 绘制两组柱状图
bars1 = ax.bar(index, recall_2, bar_width, label='Recall@2')
bars2 = ax.bar(index + bar_width, recall_5, bar_width, label='Recall@5')


# 添加文本标签、标题和图例
# ax.set_xlabel('Models')
ax.set_ylabel('Recall')
ax.set_title('Average Recall by Model')
ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(models)#, rotation=30)
ax.legend()
plt.legend()
plt.tight_layout()

# 展示图表
# plt.grid(True)
# plt.show()
plt.savefig("LLM_vs_recall.png")


#
# plt.figure(figsize=(10, 6))
#
# # plt.plot(max_iters, recall_2_usage, marker="o", label="Token Usage")
#
# # 添加标题和坐标轴标签
# plt.title("Max Iterations vs Token Usage")
# plt.xticks(max_iters)
# plt.xlabel("Max Iterations")
# plt.ylabel("Token Usage")
#
# # 显示图例
# plt.legend()
#
# # 展示图表
# plt.grid(True)
# # plt.show()
# plt.savefig("max_iter_vs_token_usage.png")
