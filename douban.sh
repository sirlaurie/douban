#!/bin/zsh

# 设置头信息
headers="Host: frodo.douban.com
Content-Type: application/json
Connection: keep-alive
Accept: */*
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac
Referer: https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html
Accept-Language: en-us"

# 搜索模式
search_mode_v=(movie tv)
search_mode_s=(music)
search_mode_b=(book)
search_mode_o=(app game event drama)
search_mode_p=(person)
search_mode_all=(${search_mode_v[@]} ${search_mode_s[@]} ${search_mode_b[@]} ${search_mode_o[@]} ${search_mode_p[@]})

# 目标URL
target_url_movie="https://movie.douban.com/subject/"
target_url_book="https://book.douban.com/subject/"
target_url_tv="https://movie.douban.com/subject/"
target_url_music="https://music.douban.com/subject/"
target_url_app="https://www.douban.com/app/"
target_url_game="https://www.douban.com/game/"
target_url_event="https://www.douban.com/event/"
target_url_drama="https://www.douban.com/drama/"

# 创建缓存目录
cache_dir="cache"
if [ ! -e $cache_dir ]; then
  mkdir -p "$cache_dir"
fi

# 清空缓存
function clear() {
  rm -rf "$cache_dir"/*
}


# 下载缩略图
function download_thumb() {
  local url=$1
  local filename=$2
  nohup curl --no-progress-meter --output-dir "$cache_dir" -o "$filename" "$url" &>/dev/null &
}

# 搜索主函数
function search() {
  clear
  local keyword=$1
  local mode=$2

  local api_url="https://frodo.douban.com/api/v2/search/weixin?q=${keyword}&start=0&count=20&apiKey=0ac44ae016490db2204ce0a042db2916"

  local result=$(curl -H "$headers" "$api_url")
  local items=$(echo "$result" | jq -r '.items // []')

  local feedback=()

  local num_items=$(echo "$items" | jq '. | length')

  for ((i=0; i<num_items; i++)); do

    local item=$(echo "$items" | jq -r ".[$i]")

    local target_type=$(echo "$item" | jq -r '.target_type')
    # local query_mode

    if [[ $mode ]]; then
      query_mode="${search_mode_$mode[@]}"
    else
      query_mode="${search_mode_all[@]}"
    fi

    if [[ " ${query_mode[@]} " =~ " ${target_type} " ]]; then

      local id=$(echo "$item" | jq -r '.target.id')
      local title=$(echo "$item" | jq -r '.target.title')
      local subtitle=$(echo "$item" | jq -r '.target.card_subtitle')
      local cover_url=$(echo "$item" | jq -r '.target.cover_url')
      local new_url="${cover_url%%\?*}"
      local cover="${new_url##*/}"
      download_thumb "$cover_url" "$cover" &>/dev/null

      local icon="$cache_dir/$cover"

      case "$target_type" in
        movie|tv) url="$target_url_movie$id" ;;
        book) url="$target_url_book$id" ;;
        music) url="$target_url_music$id" ;;
        app) url="$target_url_app$id" ;;
        game) url="$target_url_game$id" ;;
        event) url="$target_url_event$id" ;;
        drama) url="$target_url_drama$id" ;;
      esac

      local rating=$(echo "$item" | jq -r '.target.rating // {"value": -1}')
      local star=$(echo "$rating" | jq -r '.star_count // 0')

      local integer=$(echo "$star" | awk -F'.' '{print $1}')
      local decimal=$(echo "$star" | awk -F'.' '{print $2}')
      # local star_info
      if [ "$decimal" -ne "0" ]; then
        local star_info=$(printf '★%.0s' $(seq 1 $integer))
        star_info="$star_info☆"
      else
        local star_info=$(printf '★%.0s' $(seq 1 $integer))
      fi
      feedback+=("{\"uid\":\"$url\",\"title\":\"$title $star_info\",\"subtitle\":\"$subtitle\",\"arg\":\"$url\",\"quicklookurl\":\"$url\",\"icon\":{\"type\":\"file\",\"path\":\"$icon\"}}")
    fi
  done

  if [[ ${#feedback[@]} -eq 0 ]]; then
    feedback+=("{\"uid\":\"0\",\"title\":\"未能搜索到结果, 请通过豆瓣搜索页面进行搜索\",\"subtitle\":\"回车, 跳转到豆瓣\",\"args\":\"https://search.douban.com/movie/subject_search?search_text=${keyword}&cat=1002\",\"icon\":\"icon.png\"}")
  fi

  # 初始化结果字符串
  result=""

  # 遍历数组元素
  for element in "${feedback[@]}"
  do
      result="$result$element,"
  done

  # 去除最后一个逗号
  result=${result%,}

  # 生成JSON
  sleep 1
  echo "{\"items\":[$result]}"
}

if [[ $1 == "c" ]]; then
  clear
  exit
fi

keyword=$*

search "$keyword"
