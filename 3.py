import flet as ft


# 定义数据结构
class SafetyItem:
    def __init__(self, key, name, weight, is_complex=False, sub_items=None):
        self.key = key
        self.name = name
        self.weight = weight
        self.is_complex = is_complex
        self.sub_items = sub_items if sub_items else []


# JGJ59-2011 标准配置
ITEMS_CONFIG = [
    SafetyItem("manage", "安全管理", 10),
    SafetyItem("civil", "文明施工", 15),
    SafetyItem("scaffold", "脚手架", 10, is_complex=True, sub_items=[
        "扣件式钢管脚手架", "悬挑式脚手架", "门式钢管脚手架",
        "碗扣式钢管脚手架", "附着式升降脚手架", "承插型盘扣式钢管脚手架",
        "高处作业吊篮", "满堂脚手架"
    ]),
    SafetyItem("pit", "基坑工程", 10),
    SafetyItem("template", "模板支架", 10),
    SafetyItem("height", "高处作业", 10),
    SafetyItem("electric", "施工用电", 10),
    SafetyItem("hoist", "物料提升机与施工升降机", 10, is_complex=True, sub_items=[
        "物料提升机", "施工升降机"
    ]),
    SafetyItem("crane", "塔式起重机与起重吊装", 10, is_complex=True, sub_items=[
        "塔式起重机", "起重吊装"
    ]),
    SafetyItem("machinery", "施工机具", 5),
]


def main(page: ft.Page):
    page.title = "JGJ59 安全评分"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#f5f5f5"

    # 设置窗口大小
    page.window_width = 800
    page.window_height = 900
    page.window_resizable = True

    # 存储控件引用的字典
    controls_map = {}

    # --- 显示使用说明 ---
    def show_info(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(
                "使用说明：1. 每个大项可通过开关设置为缺项 2. 复杂项需勾选子项并输入得分 3. 得分输入范围为0-100分"),
            duration=3000
        )
        page.snack_bar.open = True
        page.update()

    # --- 辅助函数：创建评分卡片 ---
    def create_card(item: SafetyItem):
        # 1. 大项开关（控制是否缺项）
        switch = ft.Switch(
            value=True,
            active_color="blue",
            on_change=lambda e: toggle_section(e, item.key)
        )

        # 2. 标题行
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(item.name, size=16, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Text(f"满分: {item.weight} 分", size=12, color="grey"),
                ], spacing=2),
                switch
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
            bgcolor="white"
        )

        # 3. 内容区域
        content_area = ft.Column(visible=True)

        if not item.is_complex:
            # 简单项：直接输入分数
            score_input = ft.TextField(
                label="检查得分",
                hint_text="0-100",
                suffix_text="分",
                keyboard_type=ft.KeyboardType.NUMBER,
                border_color="blue",
                text_size=14,
                height=50,
                on_change=lambda e: validate_input(e.control),
                expand=True
            )
            content_area.controls.append(ft.Container(content=score_input, padding=10))
            controls_map[item.key] = {
                'type': 'simple',
                'weight': item.weight,
                'enabled': switch,
                'input': score_input
            }
        else:
            # 复杂项：子项列表，使用两列布局
            sub_controls = []

            # 创建两列布局
            left_column = ft.Column(spacing=5)
            right_column = ft.Column(spacing=5)

            # 计算每列应该有多少项（尽量平均分配）
            mid_index = (len(item.sub_items) + 1) // 2  # 向上取整

            # 分配子项到左右两列
            for i, sub_name in enumerate(item.sub_items):
                cb = ft.Checkbox(label=sub_name, value=False, fill_color="blue")
                tf = ft.TextField(
                    label="得分",
                    width=100,
                    height=40,
                    text_size=13,
                    content_padding=5,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    visible=False,
                    disabled=True,
                    border_color="blue",
                    on_change=lambda e: validate_input(e.control)
                )

                def on_cb_change(e, text_field=tf):
                    text_field.visible = e.control.value
                    text_field.disabled = not e.control.value
                    text_field.update()

                cb.on_change = on_cb_change

                # 创建子项行
                row = ft.Row(
                    [cb, tf],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )

                # 添加到子项控制列表
                sub_controls.append({'cb': cb, 'input': tf})

                # 根据索引分配到左列或右列
                if i < mid_index:
                    left_column.controls.append(row)
                else:
                    right_column.controls.append(row)

            # 创建两列布局的容器
            two_column_layout = ft.Row(
                [left_column, right_column],
                spacing=20,
                run_spacing=5
            )

            content_area.controls.append(
                ft.Container(content=two_column_layout, padding=ft.padding.all(10))
            )

            controls_map[item.key] = {
                'type': 'complex',
                'weight': item.weight,
                'enabled': switch,
                'subs': sub_controls
            }

        # 包装成卡片样式（使用 #AARRGGBB 透明色）
        card_container = ft.Container(
            content=ft.Column([header, ft.Divider(height=1, color="#eeeeee"), content_area], spacing=0),
            bgcolor="white",
            border_radius=10,
            margin=ft.margin.only(bottom=10, left=5, right=5, top=5),  # 调整边距适应紧凑布局
            shadow=ft.BoxShadow(blur_radius=5, color="#1A000000"),
            expand=True  # 使卡片可以扩展
        )

        switch.data = content_area
        return card_container

    # --- 输入验证函数 ---
    def validate_input(text_field: ft.TextField):
        if text_field.value:
            try:
                value = float(text_field.value)
                if value < 0:
                    text_field.value = "0"
                    text_field.update()
                elif value > 100:
                    text_field.value = "100"
                    text_field.update()
            except ValueError:
                # 如果不是数字，清空输入
                if text_field.value != "":
                    text_field.value = ""
                    text_field.update()

    # --- 交互逻辑 ---
    def toggle_section(e, key):
        switch = e.control
        content_col = switch.data
        content_col.visible = switch.value
        content_col.update()

        status = "已启用" if switch.value else "已设为缺项 (不计入总权重)"
        page.snack_bar = ft.SnackBar(ft.Text(f"{status}"), duration=1000)
        page.snack_bar.open = True
        page.update()

    # --- 核心计算逻辑 ---
    def calculate(e):
        total_weighted_score = 0.0
        valid_weight_sum = 0.0
        error_fields = []

        try:
            for key, data in controls_map.items():
                if not data['enabled'].value:
                    continue

                weight = data['weight']
                valid_weight_sum += weight

                item_score_100 = 0.0

                if data['type'] == 'simple':
                    val_str = data['input'].value
                    if val_str:
                        try:
                            item_score_100 = float(val_str)
                        except ValueError:
                            error_fields.append(data['input'])
                    else:
                        item_score_100 = 0.0
                else:
                    sub_sum = 0.0
                    sub_count = 0
                    for sub in data['subs']:
                        if sub['cb'].value:
                            val_str = sub['input'].value
                            if val_str:
                                try:
                                    val = float(val_str)
                                    sub_sum += val
                                    sub_count += 1
                                except ValueError:
                                    error_fields.append(sub['input'])
                            else:
                                error_fields.append(sub['input'])

                    if sub_count > 0:
                        item_score_100 = sub_sum / sub_count
                    else:
                        item_score_100 = 0.0

                item_score_100 = max(0, min(100, item_score_100))
                total_weighted_score += (item_score_100 / 100.0) * weight

            # 检查是否有错误输入
            if error_fields:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"发现 {len(error_fields)} 个无效输入，请检查数字格式"),
                    bgcolor="orange"
                )
                page.snack_bar.open = True
                page.update()
                return

            # 最终折算公式
            if valid_weight_sum > 0:
                final_score = (total_weighted_score / valid_weight_sum) * 100.0
            else:
                final_score = 0.0

            show_result_dialog(final_score, total_weighted_score, valid_weight_sum)

        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"计算错误: {str(ex)}"),
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()

    # --- 结果展示 ---
    def show_result_dialog(final, raw, base):
        # 判断安全等级
        if final >= 80:
            score_color = "green"
            safety_level = "优良"
        elif final >= 70:
            score_color = "orange"
            safety_level = "合格"
        else:
            score_color = "red"
            safety_level = "不合格"

        dlg = ft.AlertDialog(
            title=ft.Text("计算结果", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{final:.2f}", size=50, weight=ft.FontWeight.BOLD, color=score_color),
                        ft.Text(f"安全等级: {safety_level}", size=16, color=score_color),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center
                ),
                ft.Divider(),
                ft.Row([ft.Text("实得权重分:"), ft.Text(f"{raw:.2f}")], alignment="spaceBetween"),
                ft.Row([ft.Text("有效满分基数:"), ft.Text(f"{base:.0f}")], alignment="spaceBetween"),
                ft.Row([ft.Text("缺项扣除权重:"), ft.Text(f"{100 - base:.0f}", color="red")], alignment="spaceBetween"),
                ft.Row([ft.Text("换算系数:"), ft.Text(f"{base / 100:.3f}")], alignment="spaceBetween"),
            ], height=250, width=350, spacing=10),
            actions=[
                ft.TextButton("复制结果", on_click=lambda e: copy_result(e, final, raw, base, safety_level)),
                ft.TextButton("关闭", on_click=lambda e: close_dlg(e))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dlg(e):
        page.dialog.open = False
        page.update()

    def copy_result(e, f, r, b, level):
        result_text = f"JGJ59-2011安全评分结果：\n最终得分：{f:.2f}分\n安全等级：{level}\n实得权重分：{r:.2f}\n有效满分基数：{b:.0f}\n缺项扣除权重：{100 - b:.0f}"
        page.set_clipboard(result_text)
        page.snack_bar = ft.SnackBar(ft.Text("结果已复制到剪贴板"))
        page.snack_bar.open = True
        page.update()

    # --- 重置所有输入 ---
    def reset_all(e):
        for key, data in controls_map.items():
            data['enabled'].value = True
            data['enabled'].update()

            if 'data' in data['enabled']:  # 确保内容区域可见
                content_col = data['enabled'].data
                if content_col:
                    content_col.visible = True
                    content_col.update()

            if data['type'] == 'simple':
                data['input'].value = ""
                data['input'].update()
            else:
                for sub in data['subs']:
                    sub['cb'].value = False
                    sub['cb'].update()
                    sub['input'].value = ""
                    sub['input'].visible = False
                    sub['input'].disabled = True
                    sub['input'].update()

        page.snack_bar = ft.SnackBar(ft.Text("已重置所有输入"))
        page.snack_bar.open = True
        page.update()

    # --- 构建页面 ---
    app_bar = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("JGJ59-2011 安全评分助手", size=20, weight=ft.FontWeight.BOLD, color="white"),
                ft.IconButton(
                    icon="info",
                    icon_color="white",
                    tooltip="使用说明",
                    on_click=show_info
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("建筑施工安全检查标准评分系统", size=12, color="#CCCCCC")
        ]),
        bgcolor="#2196F3",
        padding=ft.padding.only(left=20, top=40, bottom=15, right=20),
        shadow=ft.BoxShadow(blur_radius=10, color="#4D1E3A8A")
    )

    # 说明文本
    info_text = ft.Container(
        content=ft.Column([
            ft.Text("使用说明：", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("1. 每个大项可通过开关设置为缺项（不计入总分）", size=12),
            ft.Text("2. 复杂项需勾选子项并输入得分", size=12),
            ft.Text("3. 得分输入范围为0-100分", size=12),
            ft.Text("4. 点击右下角计算按钮进行总分计算", size=12),
        ], spacing=3),
        bgcolor="#E3F2FD",
        padding=10,
        border_radius=5,
        margin=ft.margin.only(left=10, right=10, top=10, bottom=5)
    )

    # 创建所有卡片
    all_cards = {}
    for item in ITEMS_CONFIG:
        all_cards[item.key] = create_card(item)

    # 创建分组行
    # 第1行：安全管理、文明施工
    row1 = ft.Row(
        controls=[
            ft.Container(content=all_cards["manage"], expand=True),
            ft.Container(content=all_cards["civil"], expand=True),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # 第2行：脚手架（单独一行，因为内容较多）
    row2 = ft.Row(
        controls=[all_cards["scaffold"]],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # 第3行：基坑工程、模板支架
    row3 = ft.Row(
        controls=[
            ft.Container(content=all_cards["pit"], expand=True),
            ft.Container(content=all_cards["template"], expand=True),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # 第4行：高处作业、施工用电
    row4 = ft.Row(
        controls=[
            ft.Container(content=all_cards["height"], expand=True),
            ft.Container(content=all_cards["electric"], expand=True),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # 第5行：物料提升机与施工升降机、塔式起重机与起重吊装
    row5 = ft.Row(
        controls=[
            ft.Container(content=all_cards["hoist"], expand=True),
            ft.Container(content=all_cards["crane"], expand=True),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # 第6行：施工机具（单独一行）
    row6 = ft.Row(
        controls=[all_cards["machinery"]],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # 操作按钮
    buttons_row = ft.Container(
        content=ft.Row([
            ft.ElevatedButton(
                "重置所有",
                icon="refresh",
                on_click=reset_all,
                bgcolor="#FF9800",
                color="white"
            ),
            ft.ElevatedButton(
                "计算总分",
                icon="calculate",
                on_click=calculate,
                bgcolor="#2196F3",
                color="white"
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        padding=10,
        margin=ft.margin.only(bottom=10)
    )

    # 底部页脚 - 显示"安徽两淮建设技术中心"
    footer = ft.Container(
        content=ft.Column([
            ft.Divider(height=1, color="#cccccc"),
            ft.Row([
                ft.Text(
                    "安徽两淮建设技术中心",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#666666",
                    text_align=ft.TextAlign.CENTER
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Text(
                    "JGJ59-2011 建筑施工安全检查标准评分系统",
                    size=12,
                    color="#999999",
                    text_align=ft.TextAlign.CENTER
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=5),
        padding=ft.padding.only(top=10, bottom=20),
        bgcolor="#f8f8f8"
    )

    # 主容器
    main_container = ft.Column([
        info_text,
        ft.Container(
            content=ft.Column([
                row1,
                row2,
                row3,
                row4,
                row5,
                row6
            ], spacing=10),
            padding=10
        ),
        buttons_row,
        footer  # 添加页脚
    ])

    # 浮动按钮
    fab = ft.FloatingActionButton(
        icon="calculate",
        text="计算",
        bgcolor="#2196F3",
        on_click=calculate,
        tooltip="计算总分",
        shape=ft.RoundedRectangleBorder(radius=20)
    )

    page.add(
        app_bar,
        ft.Container(
            content=main_container,
            expand=True
        )
    )
    page.floating_action_button = fab
    page.floating_action_button_location = ft.FloatingActionButtonLocation.END_FLOAT


if __name__ == "__main__":
    ft.app(target=main)