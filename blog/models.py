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
    # 统计每片文章的访问量
    pv = models.PositiveIntegerField(default=1)
    uv = models.PositiveIntegerField(default=1)

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

    @classmethod
    def hot_posts(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv')

    '''
    Following relationships “backward”
    If a model has a ForeignKey, instances of the foreign-key model will have access to a Manager that returns all 
    instances of the first model. By default, this Manager is named FOO_set, where FOO is the source model name, 
    lowercased. This Manager returns QuerySets, which can be filtered and manipulated as described in the “Retrieving 
    objects” section above.
    '''

    """
    1、什么是PV值
    PV（page view）即页面浏览量或点击量，是衡量一个网站或网页用户访问量。具体的说，PV值就是所有访问者在24小时（0点到24点）内看了某个网站多少
    个页面或某个网页多少次。PV是指页面刷新的次数，每一次页面刷新，就算做一次PV流量。度量方法就是从浏览器发出一个对网络服务器的请求（Request），
    网络服务器接到这个请求后，会将该请求对应的一个网页（Page）发送给浏览器，从而产生了一个PV。那么在这里只要是这个请求发送给了浏览器，无论这个
    页面是否完全打开（下载完成），那么都是应当计为1个PV。


    2、什么是UV值
    UV（unique visitor）即独立访客数，指访问某个站点或点击某个网页的不同IP地址的人数。在同一天内，UV只记录第一次进入网站的具有独立IP的
    访问者，在同一天内再次访问该网站则不计数。UV提供了一定时间内不同观众数量的统计指标，而没有反应出网站的全面活动。

    作者：丰泽
    链接：https://juejin.im/post/5baed4baf265da0ac07c60f0
    来源：掘金
    著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
    """
