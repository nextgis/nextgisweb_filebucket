# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import webtest
import zipfile
import six

TEST_FILE1 = {"name": "red/rose.flw", "content": "rose".encode("utf-8")}
TEST_FILE2 = {"name": "orchid.flw", "content": "orchid".encode("utf-8")}
TEST_FILE3 = {"name": "white/daisy.flw", "content": "daisy".encode("utf-8")}


def test_bucket_crud(env, webapp):
    webapp.authorization = ("Basic", ("administrator", "admin"))

    resp = webapp.post("/api/component/file_upload/upload", [
        ["files[]", webtest.Upload(TEST_FILE1["name"], TEST_FILE1["content"])],
        ["files[]", webtest.Upload(TEST_FILE2["name"], TEST_FILE2["content"])],
        ["files[]", webtest.Upload(TEST_FILE3["name"], TEST_FILE3["content"])]
    ])

    data = {
        "resource": {"cls": "file_bucket", "display_name": "test-bucket", "parent": {"id": 0}},
        "file_bucket": {"files": resp.json["upload_meta"]}
    }
    resp = webapp.post_json("/api/resource/", data, status=201)
    bucket_id = resp.json["id"]

    resp = webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE1["name"]), status=200)
    assert resp.body == TEST_FILE1["content"]
    resp = webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE2["name"]), status=200)
    assert resp.body == TEST_FILE2["content"]
    resp = webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE3["name"]), status=200)
    assert resp.body == TEST_FILE3["content"]

    webapp.put_json("/api/resource/%d" % bucket_id, {
       "file_bucket": {"files": [{"name": "iam/../bad"}]}
    }, status=422)

    webapp.put_json("/api/resource/%d" % bucket_id, {
        "file_bucket": {"files": [{"name": TEST_FILE1["name"]}]}
    }, status=200)
    webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE1["name"]), status=200)
    webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE2["name"]), status=404)

    resp = webapp.post("/api/component/file_upload/upload", {
        "file": webtest.Upload(TEST_FILE1["name"], TEST_FILE1["content"]
    )})
    webapp.put_json("/api/resource/%d" % bucket_id, {
        "file_bucket": {"files": resp.json["upload_meta"]}
    }, status=200)

    webapp.delete("/api/resource/%d" % bucket_id, status=200)
    webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE3["name"]), status=404)

def test_archive(env, webapp):
    webapp.authorization = ("Basic", ("administrator", "admin"))

    def make_archive(files):
        data = six.BytesIO()
        with zipfile.ZipFile(data, mode="a", compression=zipfile.ZIP_DEFLATED, allowZip64=False) as archive:
            for f in files:
                archive.writestr(f["name"], f["content"])
        data.seek(0)

        resp = webapp.put("/api/component/file_upload/upload", data.read())
        return resp.json["id"]

    archive_id = make_archive([TEST_FILE1, TEST_FILE2])

    bucket_data = {
        "resource": {"cls": "file_bucket", "display_name": "test-bucket-from-archive", "parent": {"id": 0}},
        "file_bucket": {"archive": {"id": archive_id}, "files": []}
    }
    webapp.post_json("/api/resource/", bucket_data, status=422)

    del bucket_data["file_bucket"]["files"]
    resp = webapp.post_json("/api/resource/", bucket_data, status=201)
    bucket_id = resp.json["id"]

    resp = webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE1["name"]), status=200)
    assert resp.content_type == "text/plain"
    assert resp.body == TEST_FILE1["content"]
    resp = webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE2["name"]), status=200)
    assert resp.body == TEST_FILE2["content"]

    archive_id = make_archive([TEST_FILE2, TEST_FILE3])
    webapp.put_json("/api/resource/%d" % bucket_id, {
        "file_bucket": {"archive": {"id": archive_id}}
    }, status=200)
    webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE1["name"]), status=404)
    webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE2["name"]), status=200)
    webapp.get("/api/resource/%d/file/%s" % (bucket_id, TEST_FILE3["name"]), status=200)

    resp = webapp.get("/api/resource/%d/export" % bucket_id, status=200)
    with zipfile.ZipFile(six.BytesIO(resp.body), mode="r", compression=zipfile.ZIP_DEFLATED, allowZip64=False) as archive:
        assert archive.read(TEST_FILE2["name"]) == TEST_FILE2["content"]
        assert archive.read(TEST_FILE3["name"]) == TEST_FILE3["content"]

    webapp.delete("/api/resource/%d" % bucket_id, status=200)
