<%! from nextgisweb_filebucket.file_bucket.util import _ %>
<table class="pure-table pure-table-horizontal" style="width: 100%">
    <thead>
        <tr>
            <th style="width: 5%">#</th>
            <th style="width: 75%">${tr(_("Name"))}</th>
            <th style="width: 25%">${tr(_("MIME type"))}</th>
            <th style="width: 0%; white-space: nowrap;">${tr(_("Size, KB"))}</th>
        </tr>
    </thead>
    %for idx, fobj in enumerate(obj.files, start=1):
        <tr>
            <td>${idx}</td>
            <td>
                <a href="${request.route_url('resource.file_download', id=obj.id, name=fobj.name)}">
                ${fobj.name}
                </a>
            </td>
            <td>${fobj.mime_type}</td>
            <td>${fobj.size / 1024 if fobj.size >= 1024 else round(fobj.size / 1024.0, 3)}</td>
        </tr>
    %endfor
</table>
