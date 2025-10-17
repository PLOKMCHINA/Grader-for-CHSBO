import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import json
from datetime import datetime

class GraderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("试卷批改器")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f8ff')
        
        # 先定义变量
        self.current_file = None
        self.draft_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 批改模式变量
        self.special_mode_var = tk.BooleanVar()
        self.special_mode_score_var = tk.StringVar(value="0")  # 默认不给分
        
        # 然后设置样式和创建界面
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Title.TLabel', font=('微软雅黑', 16, 'bold'), background='#f0f8ff', foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('微软雅黑', 12, 'bold'), background='#f0f8ff', foreground='#34495e')
        style.configure('Section.TLabel', font=('微软雅黑', 11, 'bold'), background='#f0f8ff', foreground='#2c3e50')
        style.configure('Custom.TButton', font=('微软雅黑', 10), padding=6)
        style.configure('Success.TButton', font=('微软雅黑', 10), background='#27ae60', foreground='white')
        style.configure('Info.TButton', font=('微软雅黑', 10), background='#3498db', foreground='white')
        
    def create_widgets(self):
        # 主容器 - 使用PanedWindow实现可调整的分割
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧输入区域
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # 标题
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(pady=10, fill='x')
        
        title_label = ttk.Label(title_frame, text="📝 试卷批改器", style='Title.TLabel')
        title_label.pack()
        
        # 规则说明
        rule_frame = ttk.Frame(left_frame)
        rule_frame.pack(fill='x', pady=5, padx=10)
        
        rule_text = "规则说明：答案应为4位TF组合（如TTFT），如有删改可用Q或N表示"
        rule_label = ttk.Label(rule_frame, text=rule_text, font=('微软雅黑', 9), 
                              background='#fff3cd', foreground='#856404', relief='solid', padding=5)
        rule_label.pack(fill='x')
        
        # 批改模式设置
        mode_frame = ttk.LabelFrame(left_frame, text="批改模式设置", padding=10)
        mode_frame.pack(fill='x', pady=10, padx=10)
        
        # 特殊答案处理模式
        special_mode_frame = ttk.Frame(mode_frame)
        special_mode_frame.pack(fill='x', pady=5)
        
        self.special_mode_cb = ttk.Checkbutton(special_mode_frame, text="启用特殊答案处理", 
                                              variable=self.special_mode_var,
                                              command=self.toggle_special_mode)
        self.special_mode_cb.pack(side='left', padx=5)
        
        # 特殊答案得分设置
        special_score_frame = ttk.Frame(mode_frame)
        special_score_frame.pack(fill='x', pady=5)
        
        ttk.Label(special_score_frame, text="Q/N答案得分:").pack(side='left', padx=5)
        ttk.Radiobutton(special_score_frame, text="0分", variable=self.special_mode_score_var, 
                       value="0").pack(side='left', padx=5)
        ttk.Radiobutton(special_score_frame, text="2分", variable=self.special_mode_score_var, 
                       value="2").pack(side='left', padx=5)
        
        # 题目数量设置
        question_frame = ttk.Frame(mode_frame)
        question_frame.pack(fill='x', pady=5)
        
        ttk.Label(question_frame, text="题目数量:").pack(side='left', padx=5)
        self.question_count_var = tk.StringVar(value="80")
        question_entry = ttk.Entry(question_frame, textvariable=self.question_count_var, width=10)
        question_entry.pack(side='left', padx=5)
        ttk.Label(question_frame, text="题 (总分自动计算为题目数×2)").pack(side='left', padx=5)
        
        # 输入区域
        input_frame = ttk.LabelFrame(left_frame, text="答案输入区域", padding=15)
        input_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 创建左右分栏的输入区域
        input_paned = ttk.PanedWindow(input_frame, orient=tk.HORIZONTAL)
        input_paned.pack(fill='both', expand=True)
        
        # 学生答案区域
        student_frame = ttk.LabelFrame(input_paned, text="学生答案", padding=10)
        input_paned.add(student_frame, weight=1)
        
        # 学生答案文本框
        self.student_text = scrolledtext.ScrolledText(student_frame, height=20, width=40, font=('Consolas', 11))
        self.student_text.pack(fill='both', expand=True)
        
        # 正确答案区域
        correct_frame = ttk.LabelFrame(input_paned, text="正确答案", padding=10)
        input_paned.add(correct_frame, weight=1)
        
        # 正确答案文本框
        self.correct_text = scrolledtext.ScrolledText(correct_frame, height=20, width=40, font=('Consolas', 11))
        self.correct_text.pack(fill='both', expand=True)
        
        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="清空所有", command=self.clear_all, style='Custom.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="保存草稿", command=self.save_draft, style='Info.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="加载草稿", command=self.load_draft, style='Info.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="开始批改", command=self.grade_paper, style='Success.TButton').pack(side='left', padx=5)
        
        # 右侧结果显示区域
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        # 创建右侧的垂直分割
        right_paned = ttk.PanedWindow(right_frame, orient=tk.VERTICAL)
        right_paned.pack(fill='both', expand=True)
        
        # 批改结果区域
        result_frame = ttk.LabelFrame(right_paned, text="批改结果", padding=10)
        right_paned.add(result_frame, weight=2)
        
        # 统计信息
        stats_frame = ttk.Frame(result_frame)
        stats_frame.pack(fill='x', pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="等待批改...", font=('微软雅黑', 12), background='#f8f9fa')
        self.stats_label.pack(anchor='w')
        
        # 详细结果 - 使用Frame包装Treeview和滚动条
        result_tree_frame = ttk.Frame(result_frame)
        result_tree_frame.pack(fill='both', expand=True)
        
        # 创建树形视图显示详细结果
        columns = ('序号', '学生答案', '正确答案', '匹配数', '得分')
        self.result_tree = ttk.Treeview(result_tree_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        column_widths = {'序号': 60, '学生答案': 100, '正确答案': 100, '匹配数': 80, '得分': 60}
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=column_widths[col], anchor='center')
        
        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(result_tree_frame, orient='vertical', command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.result_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # 成绩分析区域
        analysis_frame = ttk.LabelFrame(right_paned, text="成绩分析", padding=10)
        right_paned.add(analysis_frame, weight=1)
        
        # 创建分析文本区域和滚动条
        analysis_text_frame = ttk.Frame(analysis_frame)
        analysis_text_frame.pack(fill='both', expand=True)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_text_frame, height=12, font=('微软雅黑', 10))
        self.analysis_text.pack(fill='both', expand=True)
        self.analysis_text.configure(state='disabled')
        
        # 底部按钮
        bottom_frame = ttk.Frame(left_frame)
        bottom_frame.pack(fill='x', pady=10)
        
        ttk.Button(bottom_frame, text="导出结果", command=self.export_results, style='Custom.TButton').pack(side='left', padx=5)
        ttk.Button(bottom_frame, text="退出程序", command=self.root.quit, style='Custom.TButton').pack(side='right', padx=5)
        
        # 添加示例数据
        self.add_sample_data()
    
    def toggle_special_mode(self):
        """切换特殊答案处理模式"""
        if self.special_mode_var.get():
            messagebox.showinfo("特殊答案处理", "已启用特殊答案处理模式：\nQ或N答案将按照选定的得分规则处理")
    
    def add_sample_data(self):
        """添加示例数据"""
        # 生成80题的示例数据
        sample_student = ""
        sample_correct = ""
        
        for i in range(1, 81):
            # 随机生成TF组合，偶尔加入Q或N
            import random
            if random.random() < 0.1:  # 10%的概率出现特殊答案
                student_ans = random.choice(['Q', 'N'])
            else:
                student_ans = ''.join(random.choice(['T', 'F']) for _ in range(4))
            
            correct_ans = ''.join(random.choice(['T', 'F']) for _ in range(4))
            sample_student += student_ans + "\n"
            sample_correct += correct_ans + "\n"
        
        self.student_text.insert('1.0', sample_student.strip())
        self.correct_text.insert('1.0', sample_correct.strip())
    
    def clear_all(self):
        """清空所有内容"""
        self.student_text.delete('1.0', tk.END)
        self.correct_text.delete('1.0', tk.END)
        self.clear_results()
    
    def clear_results(self):
        """清空结果"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.stats_label.config(text="等待批改...")
        self.analysis_text.configure(state='normal')
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.configure(state='disabled')
    
    def save_draft(self):
        """保存草稿到程序同目录"""
        student_data = self.student_text.get('1.0', tk.END).strip()
        correct_data = self.correct_text.get('1.0', tk.END).strip()
        
        if not student_data and not correct_data:
            messagebox.showwarning("警告", "没有内容可保存！")
            return
        
        draft_data = {
            'student_answers': student_data,
            'correct_answers': correct_data,
            'save_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'question_count': self.question_count_var.get(),
            'special_mode': self.special_mode_var.get(),
            'special_score': self.special_mode_score_var.get()
        }
        
        # 自动生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.draft_dir, f"试卷草稿_{timestamp}.json")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"草稿已保存到：\n{filename}")
            self.current_file = filename
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def load_draft(self):
        """从程序同目录加载草稿"""
        # 查找同目录下的所有草稿文件
        draft_files = []
        for file in os.listdir(self.draft_dir):
            if file.startswith("试卷草稿_") and file.endswith(".json"):
                file_path = os.path.join(self.draft_dir, file)
                draft_files.append((file, file_path))
        
        if not draft_files:
            messagebox.showinfo("提示", "没有找到草稿文件！")
            return
        
        # 如果只有一个草稿文件，直接加载
        if len(draft_files) == 1:
            self.load_draft_file(draft_files[0][1])
        else:
            # 多个草稿文件，让用户选择
            self.show_draft_selection(draft_files)
    
    def show_draft_selection(self, draft_files):
        """显示草稿选择窗口"""
        selection_window = tk.Toplevel(self.root)
        selection_window.title("选择草稿")
        selection_window.geometry("500x300")
        selection_window.configure(bg='#f0f8ff')
        
        ttk.Label(selection_window, text="请选择要加载的草稿文件：", style='Subtitle.TLabel').pack(pady=10)
        
        # 创建列表框
        listbox = tk.Listbox(selection_window, font=('微软雅黑', 10), height=10)
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 添加文件到列表
        for file_name, file_path in draft_files:
            listbox.insert(tk.END, file_name)
        
        # 按钮框架
        button_frame = ttk.Frame(selection_window)
        button_frame.pack(pady=10)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                selected_index = selection[0]
                selected_file = draft_files[selected_index][1]
                self.load_draft_file(selected_file)
                selection_window.destroy()
            else:
                messagebox.showwarning("警告", "请选择一个草稿文件！")
        
        ttk.Button(button_frame, text="加载选中", command=load_selected, style='Success.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="取消", command=selection_window.destroy, style='Custom.TButton').pack(side='left', padx=5)
    
    def load_draft_file(self, filename):
        """加载指定的草稿文件"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                draft_data = json.load(f)
            
            self.student_text.delete('1.0', tk.END)
            self.correct_text.delete('1.0', tk.END)
            self.student_text.insert('1.0', draft_data.get('student_answers', ''))
            self.correct_text.insert('1.0', draft_data.get('correct_answers', ''))
            
            # 加载设置
            self.question_count_var.set(draft_data.get('question_count', '80'))
            self.special_mode_var.set(draft_data.get('special_mode', False))
            self.special_mode_score_var.set(draft_data.get('special_score', '0'))
            
            self.current_file = filename
            save_time = draft_data.get('save_time', '未知时间')
            messagebox.showinfo("成功", f"草稿加载成功！\n保存时间：{save_time}")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败：{str(e)}")
    
    def calculate_score(self, student_answer, correct_answer):
        """计算单题得分"""
        # 处理特殊答案 Q 或 N
        if self.special_mode_var.get() and student_answer.upper() in ['Q', 'N']:
            return float(self.special_mode_score_var.get()), 0
        
        if len(student_answer) != 4 or len(correct_answer) != 4:
            return 0, 0
        
        matches = 0
        for s, c in zip(student_answer, correct_answer):
            if s.upper() == c.upper():
                matches += 1
        
        if matches <= 1:
            score = 0
        elif matches == 2:
            score = 0.2
        elif matches == 3:
            score = 1
        elif matches == 4:
            score = 2
        else:
            score = 0
        
        return score, matches
    
    def grade_paper(self):
        """批改试卷"""
        student_text = self.student_text.get('1.0', tk.END).strip()
        correct_text = self.correct_text.get('1.0', tk.END).strip()
        
        if not student_text or not correct_text:
            messagebox.showwarning("警告", "请填写学生答案和正确答案！")
            return
        
        # 获取题目数量
        try:
            question_count = int(self.question_count_var.get())
            if question_count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "请输入有效的题目数量！")
            return
        
        student_answers = [line.strip() for line in student_text.split('\n') if line.strip()]
        correct_answers = [line.strip() for line in correct_text.split('\n') if line.strip()]
        
        # 检查答案数量
        if len(student_answers) != question_count or len(correct_answers) != question_count:
            result = messagebox.askyesno(
                "数量不匹配", 
                f"学生答案数量({len(student_answers)})或正确答案数量({len(correct_answers)})与设置的题目数量({question_count})不匹配，是否继续批改？"
            )
            if not result:
                return
        
        # 清空之前的结果
        self.clear_results()
        
        # 批改每一题
        total_score = 0
        num_questions = min(len(student_answers), len(correct_answers), question_count)
        
        # 用于成绩分析的字典
        score_analysis = {0: [], 0.2: [], 1: [], 2: []}
        special_answers = []  # 特殊答案记录
        module_scores = {1: 0, 2: 0, 3: 0, 4: 0}  # 四个模块的得分
        module_max_scores = {1: 0, 2: 0, 3: 0, 4: 0}  # 四个模块的满分
        
        for i in range(num_questions):
            student_ans = student_answers[i] if i < len(student_answers) else ""
            correct_ans = correct_answers[i] if i < len(correct_answers) else ""
            
            # 处理特殊答案
            if self.special_mode_var.get() and student_ans.upper() in ['Q', 'N']:
                score = float(self.special_mode_score_var.get())
                matches = 0
                special_answers.append(i + 1)
            else:
                # 验证格式
                if len(student_ans) != 4 or not all(c.upper() in ['T', 'F'] for c in student_ans):
                    score, matches = 0, 0
                elif len(correct_ans) != 4 or not all(c.upper() in ['T', 'F'] for c in correct_ans):
                    score, matches = 0, 0
                else:
                    score, matches = self.calculate_score(student_ans, correct_ans)
            
            total_score += score
            
            # 记录得分情况
            score_analysis[score].append(i + 1)
            
            # 计算模块得分
            module_num = (i // 20) + 1  # 1-20:模块1, 21-40:模块2, 41-60:模块3, 61-80:模块4
            if module_num <= 4:  # 只处理前4个模块
                module_scores[module_num] += score
                module_max_scores[module_num] += 2
            
            # 添加到结果列表
            self.result_tree.insert('', 'end', values=(
                i + 1,
                student_ans,
                correct_ans,
                f"{matches}/4",
                f"{score:.1f}"
            ))
        
        # 显示统计信息
        max_score = question_count * 2  # 使用设置的题目数量计算满分
        score_rate = (total_score / max_score * 100) if max_score > 0 else 0
        
        stats_text = (f"总分: {total_score:.1f} / {max_score} | "
                     f"得分率: {score_rate:.1f}% | "
                     f"批改题数: {num_questions}")
        self.stats_label.config(text=stats_text)
        
        # 显示成绩分析
        self.show_score_analysis(score_analysis, special_answers, module_scores, module_max_scores, num_questions)
        
        # 自动滚动到最新结果
        if self.result_tree.get_children():
            self.result_tree.see(self.result_tree.get_children()[-1])
    
    def show_score_analysis(self, score_analysis, special_answers, module_scores, module_max_scores, total_questions):
        """显示成绩分析"""
        self.analysis_text.configure(state='normal')
        self.analysis_text.delete('1.0', tk.END)
        
        # 各得分情况统计
        self.analysis_text.insert('end', "各得分情况统计:\n", 'section')
        score_types = [
            (2, "2分题 (全对):"),
            (1, "1分题 (对3个):"), 
            (0.2, "0.2分题(对2个):"),
            (0, "0分题 (对0-1个):")
        ]
        
        for score, description in score_types:
            questions = score_analysis[score]
            count = len(questions)
            if count > 0:
                question_list = ', '.join(map(str, questions))  # 显示所有题号
                self.analysis_text.insert('end', f"{description:15} 共{count}题\n")
                self.analysis_text.insert('end', f"                题号: {question_list}\n")
            else:
                self.analysis_text.insert('end', f"{description:15} 无\n")
        
        self.analysis_text.insert('end', "\n")
        
        # 特殊答案统计
        if special_answers:
            self.analysis_text.insert('end', f"特殊答案(Q/N): 共{len(special_answers)}题\n", 'section')
            special_list = ', '.join(map(str, special_answers))
            self.analysis_text.insert('end', f"题号: {special_list}\n")
            self.analysis_text.insert('end', "\n")
        
        # 模块得分率分析
        self.analysis_text.insert('end', "模块得分率分析:\n", 'section')
        module_names = {
            1: "第一模块 (1-20题):",
            2: "第二模块 (21-40题):", 
            3: "第三模块 (41-60题):",
            4: "第四模块 (61-80题):"
        }
        
        for module_num in range(1, 5):
            module_name = module_names[module_num]
            score = module_scores[module_num]
            max_score = module_max_scores[module_num]
            if max_score > 0:
                rate = (score / max_score) * 100
                self.analysis_text.insert('end', f"{module_name:18} {score:.1f}/{max_score} ({rate:.1f}%)\n")
            else:
                self.analysis_text.insert('end', f"{module_name:18} 无题目\n")
        
        # 设置文本样式
        self.analysis_text.tag_configure('section', font=('微软雅黑', 11, 'bold'), foreground='#2c3e50')
        self.analysis_text.configure(state='disabled')
    
    def export_results(self):
        """导出结果到文件"""
        if not self.result_tree.get_children():
            messagebox.showwarning("警告", "没有可导出的结果！")
            return
        
        filename = os.path.join(self.draft_dir, f"批改结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("试卷批改结果\n")
                f.write("=" * 50 + "\n")
                
                # 写入详细结果
                for item in self.result_tree.get_children():
                    values = self.result_tree.item(item)['values']
                    f.write(f"第{values[0]}题: 学生答案: {values[1]}, 正确答案: {values[2]}, "
                           f"匹配: {values[3]}, 得分: {values[4]}\n")
                
                f.write("=" * 50 + "\n")
                f.write(f"{self.stats_label.cget('text')}\n")
                
                # 写入成绩分析
                f.write("\n成绩分析:\n")
                f.write("-" * 30 + "\n")
                analysis_content = self.analysis_text.get('1.0', 'end-1c')
                f.write(analysis_content)
            
            messagebox.showinfo("成功", f"结果已导出到：\n{filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

def main():
    root = tk.Tk()
    app = GraderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()