
from django.shortcuts import render, get_object_or_404, redirect

from pybo2.models import Question, Answer
from django.core.paginator import Paginator

import requests

from django.db.models import Q


def index(request):
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    question_list = Question.objects.order_by('-create_date')
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(answer__content__icontains=kw) |  # 답변 내용 검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이 검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {'question_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'pybo2/question_list.html', context)




def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'pybo2/question_detail.html', context)







def get_json_data(request):
    query = request.GET.get("search", "").strip()  # 검색어를 "search"로 받음

    # 외부 URL에서 JSON 데이터를 가져옴
    url = "https://dino-21.github.io/2025_0107/json/melon-20230906.json"
    try:
        # 외부 URL에서 JSON 데이터를 가져옴
        response = requests.get(url)
        response.raise_for_status()  # 실패하면 예외 발생

        # JSON 데이터를 딕셔너리 형태로 변환
        data = response.json()

        # 검색어가 있을 경우 필터링
        if query:
            data = [
                song for song in data
                if query.lower() in song['곡명'].lower() or query.lower() in song['가수'].lower()
            ]

        # 데이터를 템플릿에 전달
        return render(request, "pybo2/json.html", {"song_list": data, "query": query})

    except requests.exceptions.RequestException:
        # 요청이 실패했을 때 에러 메시지 표시
        error_message = "데이터를 가져오는 데 실패했습니다. 나중에 다시 시도해주세요."
        return render(request, "pybo2/json.html", {"error": error_message})
