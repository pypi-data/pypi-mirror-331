from ..common import Instance


class LabelInstance(Instance):
    TYPE = 'Label'

    def __init__(self,  **kwargs):
        """
        :attr id: ID
        :attr name: 名称
        :attr value: 值
        :attr comment: 备注
        :attr org_id: 组织 ID
        :attr org_name: 组织名称
        :attr date_created: 创建时间
        :attr date_updated: 创建时间
        :attr res_count: 资源关联数量
        """
        self.id: str = ''
        self.name: str = ''
        self.value: str = ''
        self.comment: str = ''
        self.org_id: str = ''
        self.org_name: str = ''
        self.date_created: str = ''
        self.date_updated: str = ''
        self.res_count: int = 0
        super().__init__(**kwargs)

    @property
    def display(self):
        return f'{self.name}:{self.value}'


class ResourceTypeInstance(Instance):
    TYPE = 'ResourceType'

    def __init__(self, **kwargs):
        """
        :attr id: ID
        :attr name: 名称
        :attr app_label: 应用标签
        :attr app_display: 应用标签显示名
        :attr model: 模型
        """
        self.id: str = ''
        self.name: str = ''
        self.app_label: str = ''
        self.app_display: str = ''
        self.model: str = ''
        super().__init__(**kwargs)


class LabelResourceInstance(Instance):
    TYPE = 'LabelResource'

    def __init__(self, **kwargs):
        """
        :attr id: ID
        :attr label: 标签信息
        :attr res_id: 绑定的资源 ID
        :attr res_type: 绑定的资源类型
        :attr resource: 绑定的资源名称
        :attr date_created: 创建日期
        :attr date_updated: 更新日期
        """
        self.id: str = ''
        self.label: dict = {}
        self.res_id: str = ''
        self.res_type: str = ''
        self.resource: str = ''
        self.date_created: str = ''
        self.date_updated: str = ''
        super().__init__(**kwargs)

    @property
    def display(self):
        label_display = self.label.get('display_name', '未知标签')
        return f'[{label_display}] => {self.resource}'
