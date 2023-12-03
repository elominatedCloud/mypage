from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Category, Post, Comments, User
from .forms import SignUpForm

# index.html / 메인페이지
def main(request):
    # categorys에 post_count 변수명으로 post의 개수 정보 추가
    categorys = Category.objects.annotate(post_count=Count('post'))
    # posts에 comments_count 변수명으로 comment의 개수 정보 추가 + 역순으로 출력시켜 최신순으로 보이도록 함
    posts = Post.objects.annotate(comments_count=Count('comments')).order_by('-id')

    context = {'categorys': categorys, 'posts' : posts}
    return render(request, 'mypage/index.html', context)


def signup(request):
    user_created = False  # 기본적으로 False로 설정
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # 폼을 저장하고 User 객체를 반환
            user_created = True
            # 추가적인 로직을 수행하거나 다른 페이지로 리디렉션할 수 있습니다.
            return redirect('/login')  # 리디렉션할 뷰의 이름을 지정하세요.
    else:
        form = SignUpForm()
    
    return render(request, 'mypage/signup.html', {'form': form, 'user_created': user_created})

def login_view(request):
    
    if request.method == "POST":
        username = request.POST['u_id']
        password = request.POST['u_pw']

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('/')
        else:
            print("login failed")

    return render(request, 'mypage/login.html')

def logout_view(request):

    logout(request)

    return redirect('/')

def category(request, cate_name):
    categorys = Category.objects.annotate(post_count=Count('post'))

    # 카테고리를 눌렀을 때 해당 카테고리에 포함되어 있는 post만 출력시키는 기능을 위함
    for cate in categorys:
        # cate_name이 소문자로 되어있기 때문에 lower()함수를 사용해 소문자로 변경해줌
        if cate.cate_name.lower() == cate_name:
            category_id = cate.id
    posts = Post.objects.filter(cate_id=category_id).annotate(comments_count=Count('comments')).order_by('-id')

    context = {'categorys' : categorys, 'posts' : posts, 'cate_name' : cate_name}
    return render(request, 'mypage/category.html', context)

def post_detail(request, post_id):
    # 특정 post를 클릭했을 때 해당 Post의 상세 페이지로 이동시키기 위함
    post = Post.objects.get(id=post_id)
    categorys = Category.objects.all()

    # 만약 POST method를 요청했을 때 수행되는 구문
    # 상세페이지를 들어갔을 때 DB에서 정보를 가져오기 위해 GET을 하게 되는데 해당 조건문을 달지않으면 상세페이지를 들어갈 때마다 POST를 수행하기 때문에 빈 값을 보내게 되어 오류 발생
    if request.method == "POST":
        # detail.html에 있는 input의 name값을 기반으로 value를 가져옴
        comment_content = request.POST["comment"]
        comment_id = request.POST["comment_id"]
        comment_pw = request.POST["comment_pw"]

        Comments.objects.create(
            p_id = post_id,
            c_contents = comment_content,
            c_user_id = comment_id,
            c_user_pw = comment_pw,
            c_created = timezone.now(),
            c_updated = timezone.now()
        )
        print(post_id)
        
    context = {'post' : post, 'categorys' : categorys}
    return render(request, 'mypage/detail.html', context)

# def post_write(request):
#     categorys = Category.objects.all()
#     context = {'categorys' : categorys}

#     # 위와 동일
#     if request.method == "POST":
#         cate = request.POST["categorys"]
#         title = request.POST["title"]
#         description = request.POST["description"]    
#         content = request.POST["content"]

#         # 썸네일 이미지 파일을 가져오기 위함
#         # 예외구문을 사용하지 않고 썸네일을 넣지 않는 경우 오류 발생
#         # 따라서 썸네일을 넣지 않는 경우에는 None을 입력
#         try:
#             thumbnail = request.FILES["thumbnail"]
#         except:
#             thumbnail = None

#         post = Post.objects.create(
#             cate_id = int(cate),
#             p_title = title,
#             p_desc = description,
#             p_contents = content,
#             p_created = timezone.now(),
#             p_updated = timezone.now(),
#             thumbnail = thumbnail
#         )
#         # redirect를 통해 게시글 작성을 완료하면 해당 post 상세페이지로 이동
#         return redirect(f"/posts/{post.id}")
    
#     return render(request, 'mypage/write.html', context)


@login_required  # 로그인한 사용자만 게시글 작성 가능
def post_write(request):
    categorys = Category.objects.all()
    context = {'categorys': categorys}

    if request.method == "POST":
        cate = request.POST["categorys"]
        title = request.POST["title"]
        description = request.POST["description"]
        content = request.POST["content"]

        try:
            thumbnail = request.FILES.get("thumbnail")
        except KeyError:
            thumbnail = None

        post = Post.objects.create(
            cate_id=int(cate),
            p_title=title,
            p_desc=description,
            p_contents=content,
            p_created=timezone.now(),
            p_updated=timezone.now(),
            thumbnail=thumbnail,
            author=request.user  # 현재 로그인한 사용자를 작성자로 설정
        )

        return redirect(f"/posts/{post.id}")

    return render(request, 'mypage/write.html', context)


def about(request):

    return render(request, 'mypage/about.html')

@login_required
def modify(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    categorys = Category.objects.all()

    # 게시글의 작성자가 아니면 JSON 응답을 반환합니다.
    if post.author != request.user:
        messages.error(request, "작성자가 아닌 사용자는 수정할 수 없습니다.")
        return redirect('/main')
    
    if request.method == "POST":
        # 포스트 수정 로직
        post.cate_id = request.POST["categorys"]
        post.p_title = request.POST["title"]
        post.p_desc = request.POST["description"]    
        post.p_contents = request.POST["content"]
        post.p_updated = timezone.now()

        try:
            post.thumbnail = request.FILES.get("thumbnail", post.thumbnail)
        except KeyError:
            pass

        post.save()
        return redirect(f"/posts/{post.id}")

    context = {'post': post, 'categorys': categorys}
    return render(request, 'mypage/modify.html', context)

def delete(request, post_id):
    # 해당 포스트에 대한 정보만 가져오기 위함
    post = Post.objects.get(id=post_id)
    # 해당 포스트 삭제
    post.delete()
    # 포스트를 삭제한 뒤 메인페이지로 이동
    return redirect('/')

def delete_comment(request, comments_id):
    # 해당하는 댓글에 대한 정보만 가져오기 위함
    comment = Comments.objects.get(id=comments_id)
    
    if request.method == "POST":
        c_id = request.POST["c_id"]
        c_pw = request.POST["c_pw"]

        # 입력한 아이디와 비밀번호가 등록되어있는 아이디와 비밀번호가 동일한지 확인
        # 만약 동일하다면 해당 댓글 삭제
        if c_id == comment.c_user_id and c_pw == comment.c_user_pw:
            comment.delete()

        # 댓글을 삭제한 뒤, 댓글이 있었던 포스트로 이동
        return redirect(f"/posts/{comment.p_id}")
        
    return render(request, 'mypage/comment_delete.html')