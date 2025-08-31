# 四庫全書存目叢書目錄生成工具

本工具用於將來自「京都大学 漢字情報研究センター [全國漢籍データベース](http://kanji.zinbun.kyoto-u.ac.jp/kanseki/)」 中的四庫全書存目叢書及其補編的HTML格式目錄轉換為Markdown格式，並自動生成指向維基共享資源PDF文件的鏈接。

## 使用方法

```bash
python html_to_markdown.py <input_html_file> [output_md_file]
```

### 參數說明

- `input_html_file`: 輸入的HTML檔案路徑（必需）
- `output_md_file`: 輸出的Markdown檔案路徑（可選，預設為輸入檔案同名的.md檔案）

### 使用示例

首先[檢索資料庫](http://kanji.zinbun.kyoto-u.ac.jp/kanseki?query=%E5%9B%9B%E5%BA%AB%E5%85%A8%E6%9B%B8%E5%AD%98%E7%9B%AE%E5%8F%A2%E6%9B%B8)，將結果頁面儲存下來。

注意事項：從日本資料庫下載的原始HTML檔案中可能包含少許錯誤，建議在轉換前先手動檢查和清理。

```bash
# 轉換主編HTML檔案，指定輸出檔案名
python html_to_markdown.py 四庫全書存目叢書.html 目錄.md

# 轉換補編HTML檔案
python html_to_markdown.py 四庫全書存目叢書補編.html
```

## 功能特點

- 自動識別經史子集四部分類，生成對應的PDF鏈接
- 支援多種册數格式（如：第X册、第X至Y册、第X·第Y册等）
- 四部使用三位數編號（001-999），補編使用兩位數編號（01-99）
- 自動將册數轉換為維基共享資源的PDF文件鏈接

## 輸出格式

生成的Markdown檔案包含：
- 標題層級結構
- 書目條目（粗體顯示）
- 册數資訊及對應的PDF鏈接

## 鏈接格式

- **四部**: `https://commons.wikimedia.org/wiki/File:%E5%9B%9B%E5%BA%AB%E5%85%A8%E6%9B%B8%E5%AD%98%E7%9B%AE%E5%8F%A2%E6%9B%B8[部類]XXX%E5%86%8A.pdf`
- **補編**: `https://commons.wikimedia.org/wiki/File:%E5%9B%9B%E5%BA%AB%E5%85%A8%E6%9B%B8%E5%AD%98%E7%9B%AE%E5%8F%A2%E6%9B%B8%E8%A3%9C%E7%B7%A8XX%E5%86%8A.pdf`

其中部類包括：經部、史部、子部、集部。

## 後續處理

生成的Markdown檔案需要使用其他工具（如pandoc）轉換為MediaWiki語法，然後才能貼上到維基文庫中使用。

```bash
# 使用pandoc轉換為MediaWiki格式
pandoc -f markdown -t mediawiki input.md -o output.wiki
```

## 成品鏈接

使用本工具生成的档案：

- [四庫全書存目叢書](https://frankslin.github.io/sikuquanshu-wikisource-catalog-generator/四庫全書存目叢書)
- [四庫全書存目叢書補編](https://frankslin.github.io/sikuquanshu-wikisource-catalog-generator/四庫全書存目叢書補編)

發布到維基文庫的最終成品：

- [四庫全書存目叢書](https://zh.wikisource.org/wiki/%E5%9B%9B%E5%BA%AB%E5%85%A8%E6%9B%B8%E5%AD%98%E7%9B%AE%E5%8F%A2%E6%9B%B8)
- [四庫全書存目叢書補編](https://zh.wikisource.org/wiki/%E5%9B%9B%E5%BA%AB%E5%85%A8%E6%9B%B8%E5%AD%98%E7%9B%AE%E5%8F%A2%E6%9B%B8%E8%A3%9C%E7%B7%A8)
