import requests
from bs4 import BeautifulSoup
import pymongo
from flask import Flask, request, jsonify, render_template

client = pymongo.MongoClient('localhost', 27017)
db = client.spartadb
articles = db.articles

app = Flask(__name__)

# 데이터의 흐름

# browser -> request -> api -> response -> browser

# POST
# 브라우저에서 form으로 전달 -> api endpoint(POST) -> form-data(request.form.get('url'), request.form['comment'])
# -> 크롤링을 함(requests.get(url)) -> 나온 결과 데이터를 db에 저장 -> 저장 결과를 jsonify로 json으로 만듦
# -> 다음에 브라우저로 넘겨줌

# 1. DB에는 데이터가 저장됨
# 2. 브라우저에는 api server가 준 응답이 돌아옴
# -> ajax.success: function(response)
# response : {'result': 'success', 'message': 'Good!'}

# GET
# 브라우저에서 query parameter로 request를 전달 -> api endpoint(GET) -> query parameter를 받음(request.args.get('')
# -> DB에서 찾음(db.find({}) -> 결과를 jsonify로 예쁘게 json 형태로 만듦
# -> 브라우저로 response를 넘겨줌

# 1. response에는 db에서 찾은 결과가 들어옴
# {'result': 'success', 'articles': list, object(dictionary)}


# 개발 순서
# 1. 구상 : 어떤 데이터를 가져오고, 어떻게 보여줄 것인가?
# 2. html부터 만들기(데이터를 보여주는 방법, api를 호출하는 form을 만들기)
# 3. api의 로직 만들기
# 4. api 형태로 만들기
# 유의점) 항상 request로 들어오고 response를 return 해 줘야함.
# 5. html과 api를 연결해주기($.ajax로 해결!)
# 참고) POST와 GET을 어떻게 보여줄 지 항상 고려하기!
# POST : 보통 <form> 형태로 많이 구성함
# GET은 어떻게 보여줄 지 나름

# article
# GET: 모든 article을 가져옴
    # 그러면 특정 article만 가져오고 싶을때는 어떻게 해야 하지?
    # request.args.get으로 받아서 동적으로 다른 데이터를 보여주기
# POST: 새 article을 저장함
    # 내가 URL 여러개를 한번에 넣고싶을 때는 어떻게 해야 하지?
    # 하나를 넣을 때랑, 여러 개를 넣을 때랑 프론트에서 보기에는 똑같아야 함
    # form['url']을 받되, 얘를 무조건 list로 받기
    # data: {'url': [url1])}
    # for url in urls:
        # request.get(url)..
# PUT: 특정 article을 수정함
# DELETE: 특정 article을 삭제

@app.route('/song', methods=['GET'])
def song():
    artist = request.args.get('artist')

    if not artist:
        return jsonify({'data': list(db.songs.find({}, {'_id': 0}))})
    else:
        return jsonify({'data': list(db.songs.find({'artist': artist}, {'_id': 0}))})

# <div action='/post'>
# <input type='text' name='name'>
# <input type='text' name='password'>
#
# <input type='submit'>

# submit을 누르는 순간 /post endpoint로 {'name': name.val(), 'password': password.val()}

# 포스팅박스 form에서 저장하기 버튼을 클릭하면, 저장하는 POST api를 호출하게 하기.
# 결과는 console.log로 찍으셔도 되고, alert로 찍으셔도 됩니다.

@app.route('/')
def index():
    return render_template('index.html')



# meta tag의 데이터는 포맷이 항상 똑같습니다.
# <meta property="og:..." content="....">

# POST api를 하나 만들어주세요
# form data로 url을 받습니다.
# 해당 url의 metadata를 읽어, 제목, 설명, 이미지를 가져옵니다.
# 가져온 이미지를 db에 넣습니다.
# 성공하면 성공했다고 json 메시지를 보내줍니다. 실패하면 실패했다고 json 메시지를 보내줍니다.
# TODO: 선택사항 = url을 잘 읽어서 source라는 key에 어떤 사이트에서 긁었는지 넣어주세요. 단 url을 전부 쓰시면 안되고,
# 네이버 뉴스면 'naver', platum이면 'platum'으로 저장해주서야 합니다.

# GET api를 하나 만들어주세요.
# 모든 기사 데이터를 보여줍니다.

# something = list(db.collection_name.find({}, {'_id': 0}))
# return jsonify({'result': 'success', 'data': something})

# TODO: 선택사항 = parameter로 source를 받아, 해당하는 source에서 긁어온 기사만 보여줍니다.
# ex) GET /article?source=platum -> platum에서 긁은 데이터만 보여줌



@app.route('/article', methods=['GET'])
def view_articles():
    token = request.args.get('token')
    data = list(articles.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'data': data})

# Secret asdf
# 평문 {'user': 'outtoin', expired: 2020-02-08 19:00:00}
# 평문 * secret -> asldkjfliajsefijvsladfjlijlafisjlidj
# asldkjfliajsefijvsladfjlijlafisjlidj * secret -> {'user': 'outtoin', expired: 2020-02-08 19:00:00}


# token: user 정보, expired time, 검증 로직(checksum)

@app.route('/some_very_easy_api', methods=['POST'])
def insert_article():
    url = request.form.get('url')
    comment = request.form.get('comment')
    if not url:
        return jsonify({'result': 'failure', 'message': 'No url!!'})
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'html.parser')

    # print(soup.select_one('meta[property="og:title"]')['content'])
    # print(soup.select_one('meta[property="og:description"]')['content'])
    # print(soup.select_one('meta[property="og:image"]')['content'])

    doc = {'title': soup.select_one('meta[property="og:title"]')['content'],
           'description': soup.select_one('meta[property="og:description"]')['content'],
           'image': soup.select_one('meta[property="og:image"]')['content'],
           'url': url,
           'comment': comment}

    articles.insert_one(doc)

    # return jsonify({'result': 'success'})
    return render_template('완료.html')


if __name__ == '__main__':
    # 제목 : ...
    # 이미지 URL: ...
    # 설명:

    app.run('0.0.0.0', port=5000, debug=True)
