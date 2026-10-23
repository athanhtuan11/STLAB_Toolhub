#!/usr/bin/env bash
# update-community.sh - quan ly nguon cong dong theo "Chinh sach cap nhat" (docs/COMMUNITY.md).
#
# Mac dinh CHI KIEM TRA va BAO CAO. Diem ghim chi doi khi:
#   - ban goi `apply <ten> <ref>` (tung repo mot), hoac
#   - `check --auto` voi repo allowlist=yes VA auto=on VA khong co thay doi nhay cam.
#
# Lenh:
#   status                 diem ghim, HEAD thuc te, working tree co sach khong
#   clone                  clone repo con thieu, dung o diem ghim (may moi)
#   check [ten] [--auto]   fetch, so sanh voi ban moi nhat, ghi reports/YYYY-MM-DD.md
#   apply <ten> <ref>      chuyen diem ghim sang tag/SHA <ref> (luu ghim cu de rollback)
#   rollback <ten>         quay ve diem ghim truoc
#   link                   tao symlink theo links.tsv (khong ghi de file/thu muc that)
#   verify                 kiem tra moi symlink trong links.tsv con tro dung
#   exclude                bo qua __pycache__/build trong ban clone (.git/info/exclude)
#   unlink                 xoa cac symlink trong links.tsv (truoc khi doi ten/di chuyen workspace)
set -euo pipefail

COMM="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$COMM")"
PINS="$COMM/pins.tsv"
LINKS="$COMM/links.tsv"
REPORTS="$COMM/reports"
HIST="$COMM/pin-history.log"

die() { echo "LOI: $*" >&2; exit 1; }
rows() { grep -v -e '^#' -e '^[[:space:]]*$' "$PINS"; }
row() { rows | awk -F'\t' -v n="$1" '$1==n'; }
fld() { printf '%s\n' "$1" | cut -f"$2"; }

# Ghi lai cot 4 (ref), 5 (sha), 6 (prev_sha) cua repo <ten>.
set_pin() {
  local n=$1 ref=$2 sha=$3 prev=$4 tmp
  tmp="$(mktemp)"
  awk -F'\t' -v OFS='\t' -v n="$n" -v r="$ref" -v s="$sha" -v p="$prev" \
    '$1==n && $0 !~ /^#/ {$4=r; $5=s; $6=p} {print}' "$PINS" >"$tmp"
  mv "$tmp" "$PINS"
}

tag_of() { git -C "$1" describe --tags --exact-match "$2" 2>/dev/null || echo "-"; }

# In "ref sha" cua ban moi nhat: tag on dinh moi nhat (bo dev/rc/stable...) hoac origin/HEAD.
candidate() {
  local d=$1 t=$2 tag
  if [ "$t" = tag ]; then
    tag=$(git -C "$d" tag --sort=-v:refname | grep -E '^v?[0-9]+(\.[0-9]+)*$' | head -1 || true)
    [ -n "$tag" ] || die "$d: khong tim thay tag on dinh"
    echo "$tag $(git -C "$d" rev-list -n1 "$tag")"
  else
    git -C "$d" remote set-head origin -a >/dev/null 2>&1 || true
    echo "- $(git -C "$d" rev-parse origin/HEAD)"
  fi
}

# Repo lay mot phan (co file <ten>.sparse): chi so sanh trong cac thu muc da lay, khong keo ca repo.
# PS = mang pathspec cho git diff/log.
PS=(.)
pathspec_of() {
  local f="$COMM/$1.sparse" line
  PS=(.)
  [ -f "$f" ] || return 0
  PS=()
  while IFS= read -r line; do
    line="${line%$'\r'}"
    case "$line" in ''|'#'*|'!'*) continue ;; '/*.*') PS+=(':(glob)*.*') ;; *) PS+=("${line#/}") ;; esac
  done <"$f"
}

# Thay doi nhay cam giua 2 commit: hook, MCP, quyen, phu thuoc, script/lenh shell moi.
sensitive() {
  local d=$1 a=$2 b=$3
  git -C "$d" diff --name-status "$a" "$b" -- "${PS[@]}" | awk -F'\t' '
    { st=$1; f=$NF
      if (f ~ /(^|\/)hooks\// || f ~ /hooks\.json$/)          print "HOOK        " st " " f
      else if (f ~ /(^|\/)\.mcp\.json$/)                       print "MCP         " st " " f
      else if (f ~ /settings(\.local)?\.json$/)                print "QUYEN       " st " " f
      else if (f ~ /(package(-lock)?\.json|pyproject\.toml|requirements[^\/]*\.txt|uv\.lock|Cargo\.toml|go\.mod)$/)
                                                               print "PHU-THUOC   " st " " f
      else if (st ~ /^A/ && f ~ /\.(sh|ps1|bat|cmd|py|js|mjs|ts)$/) print "SCRIPT-MOI  " st " " f
      else if (st ~ /^M/ && f ~ /\.(sh|ps1|bat|cmd)$/)         print "SHELL-DOI   " st " " f
    }'
  git -C "$d" diff -U0 "$a" "$b" -- "${PS[@]}" ':(exclude)*.lock' ':(exclude)*lock.json' \
    | grep -E '^\+[^+]' \
    | grep -i -o -E 'mcpServers|"hooks"|PreToolUse|PostToolUse|SessionStart|UserPromptSubmit|allowed-tools|"permissions"|Bash\([^)]*\)|curl |wget |Invoke-WebRequest|iex |eval\(|exec\(|subprocess|os\.system|child_process|npx |pip install|uvx ' \
    | sort | uniq -c | sort -rn | awk '{c=$1; $1=""; print "NOI-DUNG    +" c "x" $0}' || true
}

CAND_REF="" CAND_SHA="" SENS=""
check_one() {
  local r=$1 n t ref sha d sub
  n=$(fld "$r" 1); t=$(fld "$r" 3); ref=$(fld "$r" 4); sha=$(fld "$r" 5); d="$COMM/$n"
  [ -d "$d/.git" ] || { echo "## $n: CHUA CLONE"; return 0; }
  [ "$(git -C "$d" rev-parse HEAD)" = "$sha" ] || echo "> CANH BAO: HEAD khac diem ghim (chay status)"
  [ -z "$(git -C "$d" status --porcelain)" ] || echo "> CANH BAO: working tree bi sua (khong duoc sua trong repo cong dong)"
  git -C "$d" fetch --quiet --tags --force origin
  read -r CAND_REF CAND_SHA < <(candidate "$d" "$t")
  SENS=""
  if [ "$CAND_SHA" = "$sha" ]; then
    echo "## $n: khong doi ($ref ${sha:0:12})"; echo; return 0
  fi
  pathspec_of "$n"
  echo "## $n: $ref ${sha:0:12} -> $CAND_REF ${CAND_SHA:0:12}"
  [ "${PS[*]}" = "." ] || echo "- (Repo lay mot phan: chi tinh thay doi trong cac thu muc o $n.sparse)"
  echo "- So commit moi: $(git -C "$d" rev-list --count "$sha..$CAND_SHA" -- "${PS[@]}")"
  echo "- Diff: $(git -C "$d" diff --shortstat "$sha" "$CAND_SHA" -- "${PS[@]}")"
  echo; echo "### Commit (toi da 30)"; echo '```'
  git -C "$d" log --oneline --no-merges -30 "$sha..$CAND_SHA" -- "${PS[@]}"; echo '```'
  if git -C "$d" diff --quiet "$sha" "$CAND_SHA" -- CHANGELOG.md 2>/dev/null; then :; else
    echo "### CHANGELOG (dong them, toi da 40)"; echo '```'
    git -C "$d" diff "$sha" "$CAND_SHA" -- CHANGELOG.md | grep -E '^\+[^+]' | head -40 || true; echo '```'
  fi
  echo "### Phan dang lien ket vao du an"; echo '```'
  grep -v '^#' "$LINKS" | cut -f2 | grep "^community/$n/" | sort -u | while read -r sub; do
    sub="${sub#community/$n/}"
    st=$(git -C "$d" diff --shortstat "$sha" "$CAND_SHA" -- "$sub")
    echo "$sub:${st:- khong doi}"
  done; echo '```'
  SENS=$(sensitive "$d" "$sha" "$CAND_SHA")
  echo "### THAY DOI NHAY CAM"; echo '```'; echo "${SENS:-(khong co)}"; echo '```'
  echo "- Duyet xong thi ap dung: \`community/update-community.sh apply $n $([ "$CAND_REF" = - ] && echo "$CAND_SHA" || echo "$CAND_REF")\`"
  echo
}

apply_one() {
  local n=$1 want=$2 r d old new newref
  r=$(row "$n"); [ -n "$r" ] || die "khong co repo '$n' trong pins.tsv"
  d="$COMM/$n"; old=$(fld "$r" 5)
  [ -z "$(git -C "$d" status --porcelain)" ] || die "$n: working tree bi sua, dung lai"
  new=$(git -C "$d" rev-parse --verify --quiet "$want^{commit}") || die "$n: khong tim thay '$want' (chay check truoc)"
  [ "$new" != "$old" ] || { echo "$n: da o $want"; return 0; }
  git -C "$d" checkout -q --detach "$new"
  newref=$(tag_of "$d" "$new")
  set_pin "$n" "$newref" "$new" "$old"
  echo "$(date -Iseconds) apply $n ${old:0:12} -> ${new:0:12} ($newref)" >>"$HIST"
  echo "$n: ${old:0:12} -> ${new:0:12} ($newref). Rollback: community/update-community.sh rollback $n"
}

rollback_one() {
  local n=$1 r d cur prev
  r=$(row "$n"); [ -n "$r" ] || die "khong co repo '$n'"
  d="$COMM/$n"; cur=$(fld "$r" 5); prev=$(fld "$r" 6)
  [ "$prev" != "-" ] || die "$n: chua co diem ghim truoc"
  [ -z "$(git -C "$d" status --porcelain)" ] || die "$n: working tree bi sua, dung lai"
  git -C "$d" checkout -q --detach "$prev"
  set_pin "$n" "$(tag_of "$d" "$prev")" "$prev" "$cur"
  echo "$(date -Iseconds) rollback $n ${cur:0:12} -> ${prev:0:12}" >>"$HIST"
  echo "$n: da quay ve ${prev:0:12}"
}

cmd_check() {
  local only="" auto=0 out r n part
  for a in "$@"; do case "$a" in --auto) auto=1 ;; *) only=$a ;; esac; done
  mkdir -p "$REPORTS"; out="$REPORTS/$(date +%F).md"; part="$(mktemp)"
  {
    echo "# Bao cao nguon cong dong $(date '+%F %H:%M')"; echo
    echo "Chi bao cao. Khong co diem ghim nao bi doi$([ $auto = 1 ] && echo ', tru muc AUTO ben duoi')."; echo
  } >"$out"
  while IFS= read -r r; do
    n=$(fld "$r" 1)
    [ -z "$only" ] || [ "$only" = "$n" ] || continue
    # Khong pipe check_one: no phai chay trong shell hien tai de giu CAND_SHA/SENS cho buoc --auto.
    CAND_SHA="" SENS=""
    check_one "$r" >"$part"
    tee -a "$out" <"$part"
    if [ $auto = 1 ] && [ -n "$CAND_SHA" ] && [ "$(fld "$r" 7)" = yes ] && [ "$(fld "$r" 8)" = on ] && [ "$CAND_SHA" != "$(fld "$r" 5)" ]; then
      if [ -n "$SENS" ]; then
        echo "**AUTO DUNG: $n co thay doi nhay cam, can ban duyet.**" | tee -a "$out"
      else
        echo "**AUTO:** $(apply_one "$n" "$CAND_SHA")" | tee -a "$out"
      fi
    fi
  done < <(rows)
  rm -f "$part"
  echo "Da ghi: $out"
}

# Clone cac repo con thieu (vd. sau khi clone claude-workspace sang may khac), dung ngay diem ghim.
cmd_clone() {
  local r n url sha d
  while IFS= read -r r; do
    n=$(fld "$r" 1); url=$(fld "$r" 2); sha=$(fld "$r" 5); d="$COMM/$n"
    [ ! -d "$d/.git" ] || continue
    if [ -f "$COMM/$n.sparse" ]; then
      # Repo lay mot phan. Dong "# git-config key=value" trong .sparse -> git config cuc bo
      # (vd. FreeCAD-library can core.protectNTFS=false vi co ten file chua ':' nam ngoai phan lay).
      git clone -q --filter=blob:none --no-checkout --sparse "$url" "$d"
      { grep '^# git-config ' "$COMM/$n.sparse" || true; } | while read -r _ _ kv; do
        git -C "$d" config "${kv%%=*}" "${kv#*=}"
      done
      tr -d '\r' <"$COMM/$n.sparse" | git -C "$d" sparse-checkout set --no-cone --stdin
    else
      git clone -q --filter=blob:none --no-checkout "$url" "$d"
    fi
    git -C "$d" checkout -q --detach "$sha"
    echo "clone:  $n @ ${sha:0:12}"
  done < <(rows)
  cmd_exclude
}

# Bo qua file sinh ra khi addon/skill chay truc tiep tu ban clone (FreeCAD/Blender tao __pycache__).
# Chi ghi vao .git/info/exclude cuc bo, khong sua noi dung repo.
cmd_exclude() {
  local r d
  while IFS= read -r r; do
    d="$COMM/$(fld "$r" 1)"; [ -d "$d/.git" ] || continue
    for p in '__pycache__/' '*.pyc' 'build/' '*.egg-info/'; do
      grep -qxF "$p" "$d/.git/info/exclude" 2>/dev/null || echo "$p" >>"$d/.git/info/exclude"
    done
  done < <(rows)
}

cmd_status() {
  local r n sha d head
  printf '%-40s %-10s %-13s %s\n' REPO REF GHIM TRANG-THAI
  while IFS= read -r r; do
    n=$(fld "$r" 1); sha=$(fld "$r" 5); d="$COMM/$n"
    if [ ! -d "$d/.git" ]; then printf '%-40s %-10s %-13s %s\n' "$n" "$(fld "$r" 4)" "${sha:0:12}" "CHUA CLONE"; continue; fi
    head=$(git -C "$d" rev-parse HEAD)
    st="ok"; [ "$head" = "$sha" ] || st="HEAD-LECH(${head:0:12})"
    [ -z "$(git -C "$d" status --porcelain)" ] || st="$st,BI-SUA"
    printf '%-40s %-10s %-13s %s\n' "$n" "$(fld "$r" 4)" "${sha:0:12}" "$st"
  done < <(rows)
}

link_paths() { # dest src -> in "duong-dan-dest<TAB>duong-dan-src"
  local dest=$1 src=$2
  case "$dest" in "~/"*) dest="$HOME/${dest#\~/}" ;; *) dest="$ROOT/$dest" ;; esac
  printf '%s\t%s\n' "$dest" "$ROOT/$src"
}

cmd_link() {
  local dest src dp sp flag tgt
  while IFS=$'\t' read -r dest src; do
    [ -n "$dest" ] && [ "${dest:0:1}" != "#" ] || continue
    IFS=$'\t' read -r dp sp < <(link_paths "$dest" "$src")
    [ -e "$sp" ] || { echo "THIEU NGUON: $src"; continue; }
    if [ -L "$dp" ]; then echo "da co:  $dest"; continue; fi
    if [ -e "$dp" ]; then echo "BO QUA (da co file/thu muc that, khong ghi de): $dest"; continue; fi
    mkdir -p "$(dirname "$dp")"
    flag=""; [ -d "$sp" ] && flag="/D"
    # Trong workspace: link tuong doi (doi ten/di chuyen workspace khong gay). Ngoai (~/.claude): tuyet doi.
    case "$dest" in
      "~/"*) tgt="$(cygpath -w "$sp")" ;;
      *) tgt="$(realpath -m --relative-to="$(dirname "$dp")" "$sp" | tr '/' '\\')" ;;
    esac
    MSYS2_ARG_CONV_EXCL='*' cmd.exe /c mklink $flag "$(cygpath -w "$dp")" "$tgt" >/dev/null \
      && echo "tao:    $dest -> $src" || echo "LOI tao link: $dest"
  done <"$LINKS"
}

# Xoa cac symlink trong links.tsv (chi xoa symlink, khong bao gio xoa file/thu muc that).
cmd_unlink() {
  local dest src dp sp
  while IFS=$'\t' read -r dest src; do
    [ -n "$dest" ] && [ "${dest:0:1}" != "#" ] || continue
    IFS=$'\t' read -r dp sp < <(link_paths "$dest" "$src")
    [ -L "$dp" ] || continue
    if [ -d "$dp" ]; then MSYS2_ARG_CONV_EXCL='*' cmd.exe /c rmdir "$(cygpath -w "$dp")"; else rm "$dp"; fi
    echo "xoa link: $dest"
  done <"$LINKS"
}

cmd_verify() {
  local dest src dp sp bad=0
  while IFS=$'\t' read -r dest src; do
    [ -n "$dest" ] && [ "${dest:0:1}" != "#" ] || continue
    IFS=$'\t' read -r dp sp < <(link_paths "$dest" "$src")
    if [ -L "$dp" ] && [ -e "$dp" ]; then echo "ok    $dest"
    else echo "HONG  $dest"; bad=1; fi
  done <"$LINKS"
  return $bad
}

case "${1:-}" in
  status) cmd_status ;;
  clone) cmd_clone ;;
  exclude) cmd_exclude ;;
  check) shift; cmd_check "$@" ;;
  apply) [ $# -eq 3 ] || die "cach dung: apply <ten> <tag|sha>"; apply_one "$2" "$3" ;;
  rollback) [ $# -eq 2 ] || die "cach dung: rollback <ten>"; rollback_one "$2" ;;
  link) cmd_link ;;
  unlink) cmd_unlink ;;
  verify) cmd_verify ;;
  *) sed -n '2,/^set -euo/p' "$0" | grep '^#' | sed 's/^# \{0,1\}//' ;;
esac
