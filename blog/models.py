from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    name = models.CharField(max_length=128, verbose_name="名称")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    is_nav = models.BooleanField(default=False, verbose_name="是否为导航")
    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = verbose_name_plural = '分类'

    def __str__(self):
        return self.name

    @classmethod
    def get_navs(cls):
        categories = cls.objects.filter(status=Category.STATUS_NORMAL)
        """下面两行会加深IO操作，可以优化 用if判断就好"""
        # nav_categories = categories.filter(is_nav=True)
        # normal_categories = categories.filter(is_nav=False)
        nav_categories = []
        normal_categories = []
        for cate in categories:
            if cate.is_nav:
                nav_categories.append(cate)
            else:
                normal_categories.append(cate)
        return {
            'navs': nav_categories,
            'categories': normal_categories,
        }


class Tag(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除')
    )
    name = models.CharField(max_length=128, verbose_name="名称")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = verbose_name_plural = "标签"

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿')
    )
    title = models.CharField(max_length=225, verbose_name="标题")
    desc = models.CharField(max_length=1024, blank=True, verbose_name="摘要")
    content = models.TextField(verbose_name=" 正文", help_text="正文必须为MarkDown格式")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    category = models.ForeignKey(Category, verbose_name="分类", on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, verbose_name="标签", on_delete=models.CASCADE)

    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = verbose_name_plural = "文章"
        ordering = ['-id']  # 根据id 降序排列

    def __str__(self):
        return self.title

    @staticmethod
    def get_by_tag(tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            tag = None
            post_list = []
        else:
            post_list = tag.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')
        return post_list, tag

    @staticmethod
    def get_by_category(category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category = None
            post_list = []
        else:
            post_list = category.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')
        return post_list, category

    @classmethod
    def latest_post(cls):
        queryset = cls.objects.filter(status=cls.STATUS_NORMAL)
        return queryset


'''
default_related_name
Options.default_related_name
The name that will be used by default for the relation from a related object back to this one.
 The default is <model_name>_set.

This option also sets related_query_name.

As the reverse name for a field should be unique, be careful if you intend to subclass your model.
 To work around name collisions, part of the name should contain '%(app_label)s' and '%(model_name)s',
  which are replaced respectively by the name of the application the model is in, and the name of the model,
   both lowercased. See the paragraph on related names for abstract models.
'''
